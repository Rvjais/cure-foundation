# -*- coding: utf-8 -*-
"""Shared helpers + page loaders for the HTML -> PHP conversion generator."""
import collections
import glob
import os
import re

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
TAG_RE = re.compile(r'<!--.*?-->|<![^>]*>|<\?.*?\?>|<([A-Za-z][^\s/>]*)(?:\s[^>]*)?/?>', re.S)
WS_RE = re.compile(r'\s+')
STUB_TEXT = '<html><head><meta charset="utf-8"/></head><body></body></html>'

MAS_H = '<header class="site-header" id="masthead">'
MAS_E = '</header><!-- #masthead -->'
FOO_H = '<footer class="site-footer" id="colophon">'
FOO_E = '</footer><!-- #colophon -->'


def elements(s):
    """Split html into its top-level element chunks (tags, comments, text)."""
    out, i, n = [], 0, len(s)
    while i < n:
        m = TAG_RE.search(s, i)
        if not m:
            out.append(s[i:])
            break
        if m.start() > i:
            out.append(s[i:m.start()])
        raw = m.group(0)
        if raw.startswith('<!--') or raw.startswith('<!') or raw.startswith('<?'):
            out.append(raw)
            i = m.end()
            continue
        name = m.group(1).lower()
        if name in VOID or raw.endswith('/>'):
            out.append(raw)
            i = m.end()
            continue
        cm = re.compile(r'</' + re.escape(name) + r'\s*>', re.I).search(s, m.end())
        out.append(s[m.start():(cm.end() if cm else m.end())])
        i = cm.end() if cm else m.end()
    return [e for e in out if e.strip()]


def norm_head(e):
    """Normalization used to find the /common/ head elements across pages."""
    x = e.replace('../assets/', '/assets/')
    x = re.sub(r'(?<![\w/])assets/', '/assets/', x)
    x = re.sub(r'<title>.*?</title>', '<title>X</title>', x, flags=re.S)
    x = re.sub(r'https://curefoundationindia\.com/[^"\']*', 'https://curefoundationindia.com/X', x)
    x = re.sub(r'https%3A%2F%2Fcurefoundationindia\.com%2F[^"&\']*', 'URL', x)
    x = re.sub(r'\bpost-\d+\.css', 'post-X.css', x)
    x = re.sub(r'css_[0-9a-f]+\.css', 'css_X.css', x)
    x = re.sub(r'wp/v2/pages/\d+', 'wp/v2/pages/X', x)
    x = re.sub(r'\b\d{4,}\b', 'N', x)
    return x


def norm_tail(e):
    x = e.replace('../assets/', '/assets/')
    x = re.sub(r'(?<![\w/])assets/', '/assets/', x)
    x = re.sub(r'https://curefoundationindia\.com/[^"\' ]*', 'URL', x)
    x = re.sub(r'\b\d{4,}\b', 'N', x)
    x = re.sub(r'id="[^"]*\d[^"]*"', 'id="X"', x)
    return x


CUR_TOKEN_RE = re.compile(
    r'^(?:ubermenu-current|ubermenu-page_item|ubermenu-page-item|current-menu|'
    r'current_page|current-post|page_item$|page-item)')


def strip_current(s):
    """Remove baked-in menu 'current' classes / aria-current attributes."""
    def fixli(m):
        keep = [c for c in m.group(2).split() if not CUR_TOKEN_RE.match(c)]
        return m.group(1) + ' '.join(keep) + m.group(3)
    s = re.sub(r'(<li\b[^>]*\bclass=")([^"]*)(")', fixli, s)
    return s.replace(' aria-current="page"', '')


def strip_search(s):
    """Remove <div class="extras-navigation" ...>...</div> (the header search widget)."""
    i = s.find('<div class="extras-navigation"')
    if i == -1:
        return s
    depth, j = 0, i
    div_re = re.compile(r'</div>|<div\b[^>]*>', re.I)
    while True:
        m = div_re.search(s, j)
        if not m:
            raise RuntimeError('unbalanced search widget div')
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return s[:i] + s[m.end():]
        else:
            depth += 1
        j = m.end()


def base_of(path):
    b = os.path.basename(path)[:-5]  # drop .html
    return '' if b == 'index' else b


def urlpath_of_base(base):
    return '/' + base.replace('__', '/') + '/' if base else '/'


# ----------------------------------------------------------------- link rw
_ASSET_CACHE = {}
ABS_URL_RE = re.compile(r'https?://[^\s"\'<>()]+')


def _asset_exists(rel):
    rel = rel.lstrip('/')
    if rel not in _ASSET_CACHE:
        _ASSET_CACHE[rel] = os.path.isfile(rel)
    return _ASSET_CACHE[rel]


def fix_abs_url(url, full_bases):
    m = re.match(r'^(https?)://([^/?#]+)(/.*)?$', url)
    if not m:
        return url
    _scheme, host, path = m.groups()
    path = path or ''
    host_l = host.lower()
    trailing = ''
    while path and path[-1] in '.,;:!?)':
        trailing, path = path[-1] + trailing, path[:-1]
    fragment, q = '', ''
    if '#' in path:
        fragment = '#' + path.split('#', 1)[1]
        path = path.split('#', 1)[0]
    if '?' in path:
        path, q = path.split('?', 1)
        q = '?' + q
    if host_l != 'curefoundationindia.com':
        if _asset_exists('assets/_external/' + host + path):
            return '/assets/_external/' + host + path + q + fragment
        return url + trailing
    if path in ('', '/'):
        return url + trailing
    p = path.strip('/')
    name = p.replace('/', '__')
    if q in ('?ical=1', '?outlook-ical=1'):
        stub_name = name + ('__ical-1' if q == '?ical=1' else '__outlook-ical-1')
        if stub_name in full_bases:
            return '/' + p + '/' + q + fragment
    if name in full_bases:
        return '/' + p + '/' + fragment
    if _asset_exists('assets' + path):
        return '/assets' + path + q + fragment
    return url + trailing


def rw(s, full_bases):
    """Rewrite every reference that can be served locally."""
    s = s.replace('../assets/', '/assets/')
    s = s.replace('../index.html', '/')
    # mirror-root pages reference assets/... without the ../ prefix
    s = re.sub(r'(?<![\w/.-])assets/', '/assets/', s)

    def rep_attr(m):
        attr, q, val = m.group(1), m.group(2), m.group(3)
        if val.startswith(('#', '/')):
            return m.group(0)
        if val.startswith('../'):
            if val.startswith('../assets/'):
                return '%s=%s/%s%s' % (attr, q, val[3:], q)  # ../assets/x -> /assets/x
            return m.group(0)   # unexpected form: keep verbatim
        if val.startswith('assets/'):
            # root-relative mirrors (index.html) write assets/... without ../
            return '%s=%s/%s%s' % (attr, q, val, q)
        if val.startswith('pages/') and val.endswith('.html'):
            base = val[6:-5]
            if base == 'index':
                return '%s=%s/%s' % (attr, q, q)
            if re.fullmatch(r'[A-Za-z0-9_\-]+(?:__[A-Za-z0-9_\-]+)*', base) and base in full_bases:
                return '%s=%s%s%s' % (attr, q, full_bases[base], q)
        if val.endswith('.html'):
            base = val[:-5]
            if base == 'index':
                return '%s=%s/%s' % (attr, q, q)
            if re.fullmatch(r'[A-Za-z0-9_\-]+(?:__[A-Za-z0-9_\-]+)*', base) and base in full_bases:
                return '%s=%s%s%s' % (attr, q, full_bases[base], q)
        return m.group(0)

    s = re.sub(r"(\b(?:href|action|src|srcset))=([\"'])([^\"']*)\2", rep_attr, s)
    s = ABS_URL_RE.sub(lambda m: fix_abs_url(m.group(0), full_bases), s)
    return s


# ----------------------------------------------------------------- loading
def load():
    """Return (pages, stubs, meta) where pages[base] holds every extracted slot."""
    full_pages, stub_pages = [], []
    for p in ['index.html'] + sorted(glob.glob(os.path.join('pages', '*.html'))):
        with open(p, encoding='utf-8') as fh:
            t = fh.read()
        if MAS_H in t and FOO_H in t:
            full_pages.append((p, t))
        elif t == STUB_TEXT:
            stub_pages.append((p, t))
        else:
            raise RuntimeError('unknown page shape: ' + p)

    full_bases = {}
    for p, _ in full_pages:
        full_bases[base_of(p)] = urlpath_of_base(base_of(p))

    pages = {}
    for p, t in full_pages:
        b = base_of(p)
        hstart = t.find(MAS_H)
        hend = t.find(MAS_E, hstart) + len(MAS_E)
        fstart = t.find(FOO_H)
        fend = t.find(FOO_E, fstart) + len(FOO_E)
        eoff = t.rfind('</body>')
        if not (0 < hstart < hend < fstart < fend < eoff):
            raise RuntimeError('bad bounds on ' + p)
        m = re.search(r'<body[^>]*>', t)
        wp_id = None
        mm = re.search(r'\b(?:page-id|elementor-page)-(\d+)\b', m.group(0))
        if mm:
            wp_id = int(mm.group(1))
        cls = re.search(r'<body\b[^>]*\bclass="([^"]*)"', m.group(0))
        body_class = ' '.join(c for c in (cls.group(1) if cls else '').split() if c != 'has-mini-items')
        pages[b] = dict(
            path=p, base=b, urlpath=urlpath_of_base(b), wp_id=wp_id, body_class=body_class,
            title=(re.search(r'<title>(.*?)</title>', t, re.S).group(1)),
            doctype=t[:t.find('<head>')],
            html_tag=re.search(r'<html[^>]*>', t).group(0),
            head=t[t.find('<head>') + 6:t.find('</head>')],
            header=t[hstart:hend],
            content=t[hend:fstart],
            footer=t[fstart:fend],
            tail=t[fend:eoff],
            end_html=t[eoff:],
        )
    return pages, stub_pages, full_bases
