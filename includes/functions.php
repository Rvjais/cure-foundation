<?php
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
    // Flat-file pages sit in the web root: /about-us.php -> /about-us and
    // nested routes are flattened with "__" (a__b.php -> /a/b).
    if (preg_match('~^(.+)\.php$~', $h, $pm)) {
        return '/' . str_replace('__', '/', trim($pm[1], '/'));
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
    // Calendar export stubs (iCal / Outlook): /events.php?ical=1 etc.
    if (isset($_GET['ical']) || isset($_GET['outlook-ical'])) {
        cure_204();
        return;
    }

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
