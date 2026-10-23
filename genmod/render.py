# -*- coding: utf-8 -*-
"""Emits the PHP source tree (includes, pages, front controller, config)."""
import json
import os

ROOT = os.getcwd()


def php_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def php_array(d, indent='    ', int_keys=False):
    items = list(d.items()) if isinstance(d, dict) else list(enumerate(d))
    if not items:
        return 'array()'
    inner = []
    for k, v in items:
        key = k if int_keys else php_str(k)
        if isinstance(v, (dict, list)):
            inner.append('%s%s => %s,' % (indent, key, php_array(v, indent + '    ', int_keys)))
        elif v is None:
            inner.append('%s%s => NULL,' % (indent, key))
        else:
            inner.append('%s%s => %s,' % (indent, key, php_str(v)))
    return 'array(\n' + '\n'.join(inner) + '\n' + indent[:-4] + ')'


def emit(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


FUNCTIONS_PHP = r'''<?php
/**
 * Runtime helpers for the Cure Foundation site.
 *
 * Shared markup (header, UberMenu nav, footer) carries no baked-in "current
 * item" classes; they are re-assigned here per request based on the URL.
 */

/** Escape a string for HTML output. */
function e(?string $v): string
{
    return htmlspecialchars($v ?? '', ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** Normalize a path-like href for menu comparison. */
function cure_norm_path(string $href): string
{
    $h = strtolower(trim($href));
    if ($h === '') {
        return 'x';
    }
    if (preg_match('~^https?://~', $h)) {
        $p = parse_url($h, PHP_URL_PATH);
        if (!is_string($p) || $p === '') {
            return 'x'; // external URL: never matches a clean page path
        }
        $h = $p;
    }
    $q = strpos($h, '?');
    if ($q !== false) {
        return 'x'; // stub exporter links never match plain page paths
    }
    if (preg_match('~\.[A-Za-z0-9]{1,6}$~', $h)) {
        return 'x'; // asset / file link
    }
    return '/' . trim($h, '/');
}

/** Parse <li ...> / </li> tokens into items with parent links and extents. */
function cure_li_items(string $html): array
{
    if (!preg_match_all('/<li\b[^>]*>|<\/li\s*>/i', $html, $m, PREG_OFFSET_CAPTURE)) {
        return array();
    }
    $items = array();
    $stack = array();
    foreach ($m[0] as $t) {
        $tok = $t[0];
        $pos = $t[1];
        if ($tok[1] === '/') {
            if ($stack) {
                $items[$stack[count($stack) - 1]]['close'] = $pos;
                array_pop($stack);
            }
        } else {
            $items[] = array(
                'open_pos' => $pos,
                'raw'      => $tok,
                'close'    => null,
                'parent'   => $stack ? $stack[count($stack) - 1] : null,
                'anchors'  => array(),
                'anchor_tags' => array(),
                'span0'    => 0,
                'self'     => false,
                'desc'     => false,
            );
            $stack[] = count($items) - 1;
        }
    }
    return $items;
}

/** Mark li items (and their anchors) as "current" exactly like WordPress. */
function mark_current_menu(string $html, string $current_url, ?int $wp_id = null): string
{
    $cur = cure_norm_path($current_url);
    $cands = array($cur);
    if (preg_match('~^(.*?)/page/\d+/?$~', $cur, $cm)) {
        // paginated archives (/page/N/, /slug/page/N/) mark the base page item
        $cands[] = $cm[1] === '' ? '/' : '/' . trim($cm[1], '/');
    }
    $items = cure_li_items($html);
    if (!$items) {
        return $html;
    }

    foreach ($items as $idx => $it) {
        $span = substr($html, $it['open_pos'] + strlen($it['raw']),
                       max(0, ($it['close'] ?? strlen($html)) - $it['open_pos'] - strlen($it['raw'])));
        $it['span0'] = $it['open_pos'] + strlen($it['raw']);
        if (preg_match_all('/<a\b[^>]*\bhref="([^"]*)"/i', $span, $am, PREG_OFFSET_CAPTURE)) {
            $it['anchors'] = $am[1];      // captured href values (+offsets within span)
            $it['anchor_tags'] = $am[0];  // full <a> tags (+offsets within span)
        }
        $nested = stripos($span, '<li');
        if ($it['anchors'] && ($nested === false || $it['anchor_tags'][0][1] < $nested)) {
            $it['self'] = in_array(cure_norm_path($it['anchors'][0][0]), $cands, true);
        }
        foreach ($it['anchors'] as $a) {
            if (in_array(cure_norm_path($a[0]), $cands, true)) {
                $it['desc'] = true;
                break;
            }
        }
        $items[$idx] = $it;
    }

    // Phantom self: non-anchor wrapper li whose direct children all link "here"
    foreach ($items as $idx => $it) {
        if ($it['self'] || $it['anchors']) {
            continue;
        }
        $child_all_self = false;
        foreach ($items as $c) {
            if ($c['parent'] !== $idx) {
                continue;
            }
            if (!$c['self']) {
                $child_all_self = false;
                break;
            }
            $child_all_self = true;
        }
        if ($child_all_self) {
            $items[$idx]['self'] = true;
        }
    }

    $self_ids = array();
    foreach ($items as $idx => $it) {
        if ($it['self']) {
            $self_ids[] = $idx;
        }
    }
    if (!$self_ids) {
        return $html;
    }

    // parents / ancestors of the self items
    $is_parent = array();
    $is_ancestor = array();
    foreach ($self_ids as $idx) {
        $p = $items[$idx]['parent'];
        $first = true;
        while ($p !== null) {
            if ($first) {
                $is_parent[$p] = true;
                $first = false;
            }
            $is_ancestor[$p] = true;
            $p = $items[$p]['parent'];
        }
    }

    // edits in reverse open-position order so byte offsets stay valid
    uasort($items, static function ($a, $b) {
        return $b['open_pos'] <=> $a['open_pos'];
    });
    $is_page_item = static function ($classes): bool {
        return in_array('ubermenu-item-type-post_type', $classes, true)
            && in_array('ubermenu-item-object-page', $classes, true);
    };
    foreach ($items as $idx => $it) {
        $adds = array();
        $shift = 0;
        $open = substr($html, $it['open_pos'], strlen($it['raw']));
        if (!preg_match('#^(<li\b[^>]*\bclass=")([^"]*)(")#i', $open, $cm)) {
            continue;
        }
        $have = preg_split('/\s+/', trim($cm[2]));
        $is_uber = in_array('ubermenu-item', $have, true);

        if ($it['self']) {
            if ($is_uber) {
                $adds = array('ubermenu-current-menu-item');
                if (in_array('ubermenu-item-type-post_type', $have, true)
                    && in_array('ubermenu-item-object-page', $have, true)) {
                    if ($wp_id) {
                        $adds[] = 'ubermenu-page_item';
                        $adds[] = 'ubermenu-page-item-' . $wp_id;
                    }
                    $adds[] = 'ubermenu-current_page_item';
                }
            } else {
                $adds = array('current-menu-item');
                if (in_array('menu-item-object-page', $have, true)) {
                    if ($wp_id) {
                        $adds[] = 'page_item';
                        $adds[] = 'page-item-' . $wp_id;
                    }
                    $adds[] = 'current_page_item';
                }
            }
            // duplicate menu entries for the same page (e.g. the "Videos"
            // flyout wrapper): a self item that parents another self item
            // also carries the parent/ancestor markers
            if (isset($is_parent[$idx])) {
                if ($is_uber) {
                    $adds[] = 'ubermenu-current-menu-parent';
                    $adds[] = 'ubermenu-current-menu-ancestor';
                    if ($is_page_item($have)) {
                        $adds[] = 'ubermenu-current_page_parent';
                        $adds[] = 'ubermenu-current_page_ancestor';
                    }
                } else {
                    $adds[] = 'current-menu-parent';
                    $adds[] = 'current-menu-ancestor';
                }
            } elseif (isset($is_ancestor[$idx])) {
                $adds[] = $is_uber ? 'ubermenu-current-menu-ancestor' : 'current-menu-ancestor';
            }
        } elseif (isset($is_parent[$idx])) {
            if ($is_uber) {
                $adds = array('ubermenu-current-menu-parent', 'ubermenu-current-menu-ancestor');
                if ($is_page_item($have)) {
                    $adds[] = 'ubermenu-current_page_parent';
                    $adds[] = 'ubermenu-current_page_ancestor';
                }
            } else {
                $adds = array('current-menu-parent', 'current-menu-ancestor');
            }
        } elseif (isset($is_ancestor[$idx])) {
            $adds = array($is_uber ? 'ubermenu-current-menu-ancestor' : 'current-menu-ancestor');
            if ($is_uber && $is_page_item($have)) {
                $adds[] = 'ubermenu-current_page_ancestor';
            }
        }
        if ($adds) {
            $new = implode(' ', array_values(array_unique(array_merge($have, $adds))));
            if ($new !== trim($cm[2])) {
                $newstr = $cm[1] . $new . $cm[3];
                $shift = strlen($newstr) - strlen($cm[0]);
                $html = substr_replace(
                    $html,
                    $newstr,
                    $it['open_pos'],
                    strlen($cm[0])
                );
            }
        }
        if (!$is_uber && $it['self'] && $it['anchor_tags']) {
            // WP (footer) menu anchors get aria-current="page" right after <a>
            $abs = $it['span0'] + $shift + $it['anchor_tags'][0][1];
            $raw = $it['anchor_tags'][0][0];
            $ins = strpos($raw, '>');
            if ($ins !== false) {
                $html = substr_replace($html, ' aria-current="page"', $abs + $ins, 0);
            }
        }
    }
    return $html;
}

/** Empty HTTP 204 response (the iCal/Outlook export stubs). */
function cure_204(): void
{
    http_response_code(204);
    header('Content-Type: text/calendar; charset=utf-8');
}

/** Is $tok one of the WordPress/UberMenu "current item" class tokens? */
function cure_is_current_token(string $tok): bool
{
    return (bool) preg_match(
        '~^(?:ubermenu-current|ubermenu-page_item|ubermenu-page-item|'
        . 'current-menu|current_page|current-post|page_item$|page-item)~',
        $tok
    );
}

/**
 * Replay the per-page "current" class tokens baked into the original markup.
 * Only the handful of pages whose classes depend on the WP object graph
 * (single-post pages, non-anchor page wrappers) carry overrides.
 */
function cure_apply_menu_overrides(string $html, array $map): string
{
    foreach ($map as $mid => $tokens) {
        if (!preg_match('/<li\\b[^>]*\\bid="menu-item-' . preg_quote((string) $mid, '/') . '"[^>]*>/i', $html, $m)) {
            continue;
        }
        $open = $m[0];
        if (!preg_match('#^(<li\\b[^>]*\\bclass=")([^"]*)(")#i', $open, $cm)) {
            continue;
        }
        $kept = array();
        foreach (preg_split('/\\s+/', trim($cm[2])) as $tok) {
            if ($tok !== '' && !cure_is_current_token($tok)) {
                $kept[] = $tok;
            }
        }
        $merged = array_values(array_unique(array_merge($kept, preg_split('/\\s+/', $tokens))));
        $html = substr_replace(
            $html,
            $cm[1] . implode(' ', $merged) . $cm[3],
            strpos($html, $open),
            strlen($cm[0])
        );
    }
    return $html;
}

/**
 * Front controller: route and serve the current request.
 */
function cure_dispatch(): void
{
    global $CURE_ROUTES;

    $parts = explode('?', $_SERVER['REQUEST_URI'] ?? '/', 2);
    $path  = rawurldecode($parts[0]);
    $qs    = $parts[1] ?? '';

    // Legacy URLs from the static mirror keep working (redirected to clean URLs)
    if (preg_match('~^/index\.html$~i', $path)) {
        header('Location: /', true, 301);
        exit;
    }
    if (preg_match('~^/pages/([^/?]+)\.html$~i', $path, $pm)) {
        header('Location: /' . str_replace('__', '/', $pm[1]) . '/', true, 301);
        exit;
    }
    if ($qs === '' && !preg_match('~\.[A-Za-z0-9]{1,6}$~', $path)
        && $path !== '/' && substr($path, -1) !== '/') {
        header('Location: /' . trim($path, '/') . '/', true, 301);
        exit;
    }

    $key = $path . ($qs !== '' ? '?' . $qs : '');
    if (isset($CURE_ROUTES[$key])) {
        require CURE_ROOT . '/' . $CURE_ROUTES[$key];
        exit;
    }

    http_response_code(404);
    require CURE_ROOT . '/404.php';
    exit;
}

/**
 * Shared <head>: static inventory + per-page dynamic slots + gap extras.
 */
function cure_render_head(array $page): void
{
    global $CURE_HTML_SHELL;

    echo $CURE_HTML_SHELL;
    $common = include __DIR__ . '/head-common.php';
    $ex  = $page['head_extra'] ?? array();
    $dyn = $page['head_dyn']   ?? array();
    if (isset($ex[-1])) {
        echo $ex[-1];
        echo "\n";
    }
    foreach ($common as $i => $el) {
        echo ($el === null) ? ($dyn[$i] ?? '') : $el;
        echo "\n";
        if (isset($ex[$i])) {
            echo $ex[$i];
            echo "\n";
        }
    }
    echo "</head>\n";
}

/**
 * Shared markup printed after the page footer (scripts, popups).
 */
function cure_render_tail(array $page): void
{
    global $CURE_END_HTML;

    $common = include __DIR__ . '/tail-common.php';
    $ex  = $page['tail_extra'] ?? array();
    $dyn = $page['tail_dyn']   ?? array();
    if (isset($ex[-1])) {
        echo $ex[-1];
        echo "\n";
    }
    foreach ($common as $i => $el) {
        echo ($el === null) ? ($dyn[$i] ?? '') : $el;
        echo "\n";
        if (isset($ex[$i])) {
            echo $ex[$i];
            echo "\n";
        }
    }
    echo $CURE_END_HTML;
}

/**
 * Render one full page: head, header/nav, content, footer, tail.
 */
function cure_render_page(array $page): void
{
    cure_render_head($page);
    echo '<body class="' . e($page['body_class'] ?? '') . '">' . "\n";
    // wrapper around the whole page content, present on every source page
    echo '<div class="site" id="page">' . "\n";

    // Two header markup variants exist in the source mirror (they differ only
    // in the logo image attributes); header_v picks the matching one.
    $variant = (int) ($page['header_v'] ?? 1);
    if ($variant < 1 || $variant > 3) {
        $variant = 1;
    }

    ob_start();
    require __DIR__ . '/header-' . $variant . '.php';
    $header_html = ob_get_clean();

    ob_start();
    require __DIR__ . '/footer.php';
    $footer_html = ob_get_clean();

    $url   = $page['url'] ?? '/';
    $wp_id = $page['wp_id'] ?? null;
    $header_html = mark_current_menu($header_html, $url, $wp_id);
    $footer_html = mark_current_menu($footer_html, $url, $wp_id);

    global $CURE_MENU_OVERRIDES;
    if (!empty($CURE_MENU_OVERRIDES[$url])) {
        $ov = $CURE_MENU_OVERRIDES[$url];
        $header_html = cure_apply_menu_overrides($header_html, $ov);
        $footer_html = cure_apply_menu_overrides($footer_html, $ov);
    }

    echo $header_html;
    echo $page['content'] ?? '';
    echo $footer_html;

    cure_render_tail($page);
}
'''

HEAD_PHP = '''<?php
/*
 * Shared <head> element inventory.
 * Elements marked NULL vary per page (title, canonical, post CSS, ...);
 * each page supplies its own copy through 'head_dyn'.
 * Generated by the conversion generator.
 */

return '''

TAIL_PHP = '''<?php
/*
 * Shared markup after </footer> -- popups and scripts.
 * NULL slots are dynamic, supplied per page as 'tail_dyn'.
 * Generated by the conversion generator.
 */

return '''


def emit_includes(head_states, tail_states, header_variants, footer_shared, doctype, html_tag):
    emit('includes/head-common.php', HEAD_PHP + php_array(head_states, '    ', int_keys=True) + ';\n')
    emit('includes/tail-common.php', TAIL_PHP + php_array(tail_states, '    ', int_keys=True) + ';\n')
    emit('includes/functions.php', FUNCTIONS_PHP)
    for i, frag in enumerate(header_variants, 1):
        emit('includes/header-%d.php' % i,
             "<?php\n/* Shared header variant %d (topbar + branding + UberMenu). Generated. */\n?>\n" % i
             + frag + "\n")
    emit('includes/footer.php',
         "<?php\n/* Shared footer. Generated. */\n?>\n" + footer_shared)


def emit_config(routes, doctype, html_tag, end_html, overrides=None):
    shell = doctype + '<head>' + "\n"
    emit('includes/config.php', CONFIG_PHP % (
        php_array(routes, '    '),
        php_str(shell),
        php_str(end_html),
        php_array(overrides or {}, '    '),
    ))
    emit('includes/bootstrap.php', BOOTSTRAP_PHP)
    emit('api/index.php', API_PHP)
    emit('router.php', ROUTER_PHP)
    emit('.htaccess', HTACCESS)
    emit('404.php', PAGE_404)
    emit('vercel.json', json.dumps(VERCEL_JSON, indent=2) + '\n')


CONFIG_PHP = r'''<?php
/**
 * Configuration for the generated PHP site.
 * $CURE_ROUTES maps clean URLs (optionally with ?query) to include paths.
 * $CURE_MENU_OVERRIDES holds per-page menu "current item" class tokens for
 * the few pages whose classes only the WordPress object graph can compute
 * (single-post pages under a category, non-anchor page wrappers).
 */

defined('CURE_ROOT') || define('CURE_ROOT', dirname(__DIR__));

$CURE_ROUTES = %s;

$CURE_HTML_SHELL = %s;
$CURE_END_HTML   = %s;

$CURE_MENU_OVERRIDES = %s;
'''

BOOTSTRAP_PHP = r'''<?php
/**
 * Bootstrap: load config + functions. Required by every page include.
 */

require_once __DIR__ . '/config.php';
require_once __DIR__ . '/functions.php';
'''

API_PHP = r'''<?php
/**
 * Front controller (Vercel via vercel.json, Apache via .htaccess,
 * PHP built-in server via router.php).
 */

require_once dirname(__DIR__) . '/includes/bootstrap.php';
cure_dispatch();
'''

ROUTER_PHP = r'''<?php
/**
 * Router for the PHP built-in development server:
 *   php -S localhost:8000 router.php
 */

$root = __DIR__;
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';

// Internal modules end up here via API (routes / not the front controller design),
// and legacy *.html mirrors route to the front controller's 301 redirects.
$internal = preg_match('~^/(pages|includes)/~', $path)
    || preg_match('~\.html$~i', $path)
    || ($path[1] ?? '') === '_';
if (!$internal && $path !== '/' && is_file($root . $path)) {
    return false;  // let php -S serve the static file directly
}

require __DIR__ . '/api/index.php';
'''

HTACCESS = r'''# Cure Foundation India site
# Apache front controller (Vercel uses vercel.json, php -S uses router.php).

<IfModule mod_rewrite.c>
    RewriteEngine On

    # Internal PHP modules are never served directly
    RewriteRule ^/?includes/ - [F,L]
    RewriteRule ^/?pages/    - [F,L]
    RewriteRule ^/?_         - [F,L]

    # Serve real files and folders as-is (assets, favicon, ...)
    RewriteCond %{REQUEST_FILENAME} -f [OR]
    RewriteCond %{REQUEST_FILENAME} -d
    RewriteRule ^ - [L]

    # Legacy mirror URLs (/index.html, /pages/<slug>.html) are handled by the
    # front controller, which 301-redirects them to the clean URL.
    RewriteRule ^(index\.html|pages/[^/]+\.html)$ api/index.php [L]

    # Everything else goes through the front controller too
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ api/index.php [QSA,L]
</IfModule>
'''

PAGE_404 = r'''<?php
/**
 * 404 page, rendered through the shared header/footer.
 */

if (!defined('CURE_ROOT')) {
    require_once __DIR__ . '/includes/bootstrap.php';
}

cure_render_page(array(
    'url'        => '/__404__',
    'wp_id'      => null,
    'body_class' => 'error404',
    'head_dyn'   => array(),
    'head_extra' => array(),
    'content'    => <<<'CURE_404_EOF'
<div class="content-area">
    <div class="container">
        <div style="padding:64px 0;text-align:center;">
            <h1>Page not found</h1>
            <p>The page you requested could not be found.</p>
            <p><a href="/">Back to the home page</a></p>
        </div>
    </div>
</div>
CURE_404_EOF,
    'tail_dyn'   => array(),
    'tail_extra' => array(),
));
'''

VERCEL_JSON = {
    "functions": {
        "api/index.php": {
            "runtime": "vercel-php@0.9.0",
            "includeFiles": "includes/**, pages/**, index.php, 404.php"
        }
    },
    "routes": [
        {"src": "/assets/(.*)", "dest": "/assets/$1"},
        {"src": "/(.*)", "dest": "/api/index.php"}
    ]
}


def emit_page(base, page, head_states, tail_states):
    """Write pages/<base>.php (or root index.php) containing per-page slots."""
    if base and page['path'] != 'index.html':
        out = 'pages/%s.php' % base
        rel = "__DIR__ . '/../includes/bootstrap.php'"
    else:
        out = 'index.php'
        rel = "__DIR__ . '/includes/bootstrap.php'"

    head_dyn = {i: page['head_slot'][i] for i, v in enumerate(head_states) if v is None and page['head_slot'].get(i)}
    head_extra = {g: v for g, v in page['head_extra'].items() if v}
    tail_dyn = {i: page['tail_slot'][i] for i, v in enumerate(tail_states) if v is None and page['tail_slot'].get(i)}
    tail_extra = {g: v for g, v in page['tail_extra'].items() if v}
    header_v = (page.get('header_v', 0) or 0) + 1  # 1-based

    content = page['content']
    if 'CURE_PAGE_EOF' in content:
        raise RuntimeError('nowdoc terminator collision in ' + page['path'])

    title = page['title'].split(' – ')[0].strip() or base or 'Home'
    doc = "%s — clean URL: %s%s" % (
        title, page['urlpath'],
        ' (WP page %d)' % page['wp_id'] if page['wp_id'] else '')
    body = (
        "<?php\n"
        "/**\n"
        " * %s\n"
        " * Generated by the conversion generator.\n"
        " */\n\n"
        "require_once %s;\n\n"
        "cure_render_page(array(\n"
        "    'url'        => %s,\n"
        "    'wp_id'      => %s,\n"
        "    'header_v'   => %s,\n"
        "    'body_class' => %s,\n"
        "    'head_dyn'   => %s,\n"
        "    'head_extra' => %s,\n"
        "    'content'    => <<<'CURE_PAGE_EOF'\n"
        "%s\n"
        "CURE_PAGE_EOF,\n"
        "    'tail_dyn'   => %s,\n"
        "    'tail_extra' => %s,\n"
        "));\n"
    ) % (
        doc, rel,
        php_str(page['urlpath']),
        repr(page['wp_id']) if page['wp_id'] is not None else 'null',
        header_v,
        php_str(page['body_class']),
        php_array(head_dyn, '    ', int_keys=True),
        php_array({int(k): v for k, v in head_extra.items()}, '    ', int_keys=True),
        content,
        php_array(tail_dyn, '    ', int_keys=True),
        php_array({int(k): v for k, v in tail_extra.items()}, '    ', int_keys=True),
    )
    emit(out, body)


def emit_stub(name):
    emit('pages/%s.php' % name,
         "<?php\n"
         "/**\n"
         " * iCal export stub (empty feed).\n"
         " * The mirror page served an empty body; the live site returns HTTP 204\n"
         " * with no content for these calendar export URLs.\n"
         " */\n\n"
         "require_once __DIR__ . '/../includes/bootstrap.php';\n\n"
         "cure_204();\n")


def build_routes(full_bases, stub_names):
    routes = {'/': 'index.php'}
    for b in sorted(full_bases):
        if not b:
            continue  # homepage is index.php at the repo root, already routed
        routes[full_bases[b]] = 'pages/%s.php' % b
    for name in sorted(stub_names):
        segs = name.split('__')
        queries = []
        while segs and segs[-1] in ('ical-1', 'outlook-ical-1'):
            key = 'outlook-ical' if segs[-1].startswith('outlook') else 'ical'
            queries.insert(0, key + '=1')
            segs.pop()
        query = '&'.join(queries)
        include = 'pages/%s.php' % name
        path = '/' + '/'.join(segs) if segs else '/'
        if query:
            routes[path + '?' + query] = include
            if path != '/':
                routes[path + '/' + '?' + query] = include
        else:
            routes[path + '/'] = include
    return routes
