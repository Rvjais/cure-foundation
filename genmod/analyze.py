# -*- coding: utf-8 -*-
"""Aligns per-page heads/tails against the common slot inventory."""
import collections
import re

from .staticdata import CUR_TOKEN_RE, elements, norm_head, norm_tail, rw, strip_current, strip_search


def _ws(s):
    return re.sub(r'\s+', ' ', s)


def align(seq_norms, common_norms, els):
    """Walk the page element list; return (extras: gap -> [raw], slot: i -> raw)."""
    j, extras, slot = 0, collections.defaultdict(list), {}
    for i, rn in enumerate(common_norms):
        k = j
        while k < len(els) and seq_norms[k] != rn:
            extras[i - 1].append(els[k])
            k += 1
        if k >= len(els):
            return None
        slot[i] = els[k]
        j = k + 1
    last = len(common_norms) - 1
    for e in els[j:]:
        extras[last].append(e)
    return extras, slot


def analyze(pages, full_bases):
    """Fills each page with head/tail slots + extras, returns (head_states, tail_states, info)."""
    ref = pages[''] if '' in pages else pages['about-us']

    # detect header markup variants (source pages differ only in the logo
    # <img> attributes; the UberMenu nav is identical in all variants)
    seen = collections.OrderedDict()   # normalized fragment -> variant index (0-based)
    frag_by_index = {}
    for b, pg in pages.items():
        frag = strip_current(rw(strip_search(pg['header']), full_bases))
        norm = re.sub(r'\s+', ' ', frag)
        if norm not in seen:
            seen[norm] = len(seen)
        pg['header_v'] = seen[norm]
        if seen[norm] not in frag_by_index:
            frag_by_index[seen[norm]] = frag
    variants = [frag_by_index[i] for i in range(len(seen))]

    info = {'header_variants': variants}

    # shared footer (one variant expected; other variants would be reported)
    footer_shared = strip_current(rw(ref['footer'], full_bases))
    footer_diff = []
    for b, pg in pages.items():
        if re.sub(r'\s+', ' ', strip_current(rw(pg['footer'], full_bases))) != re.sub(r'\s+', ' ', footer_shared):
            footer_diff.append(b)
    info['footer_shared'] = footer_shared
    info['footer_diff'] = footer_diff

    # ---------------- common head slots ----------------
    ref_e = elements(ref['head'])
    ref_n = [norm_head(e) for e in ref_e]
    cnt = collections.Counter()
    for pg in pages.values():
        cnt.update(set(norm_head(e) for e in elements(pg['head'])))
    common_set = set(n for n, c in cnt.items() if c == len(pages))
    common_norms = [ref_n[i] for i, n in enumerate(ref_n) if n in common_set]

    head_states = [None] * len(common_norms)
    slotmeta = [dict() for _ in common_norms]
    mis = []
    for b, pg in pages.items():
        els = elements(pg['head'])
        res = align([norm_head(e) for e in els], common_norms, els)
        if res is None:
            mis.append(('head', b))
            continue
        extras, slot = res
        pg['head_slot_raw'] = slot
        pg['head_extra_raw'] = extras
        for i in range(len(common_norms)):
            slotmeta[i][slot[i]] = 1
    if mis:
        return None, None, {'mis': mis}
    for i in range(len(common_norms)):
        if len(slotmeta[i]) == 1:
            head_states[i] = rw(next(iter(slotmeta[i])), full_bases)
    # final normalized per-page dynamic slot values + extras + content
    for b, pg in pages.items():
        pg['head_slot'] = {i: rw(v, full_bases) for i, v in pg['head_slot_raw'].items()
                           if head_states[i] is None and v}
        pg['head_extra'] = {g: rw('\n'.join(v), full_bases) for g, v in pg['head_extra_raw'].items() if v}
        pg['content'] = rw(pg['content'], full_bases)

    # ---------------- common tail slots ----------------
    tref_e = elements(ref['tail'])
    tref_n = [norm_tail(e) for e in tref_e]
    tcnt = collections.Counter()
    for pg in pages.values():
        tcnt.update(set(norm_tail(e) for e in elements(pg['tail'])))
    tset = set(n for n, c in tcnt.items() if c == len(pages))
    tnorms = [tref_n[i] for i, n in enumerate(tref_n) if n in tset]

    tail_states = [None] * len(tnorms)
    tseen = [dict() for _ in tnorms]
    tmis = []
    for b, pg in pages.items():
        els = elements(pg['tail'])
        res = align([norm_tail(e) for e in els], tnorms, els)
        if res is None:
            tmis.append(('tail', b))
            continue
        extras, slot = res
        pg['tail_slot_raw'] = slot
        pg['tail_extra_raw'] = extras
        for i in range(len(tnorms)):
            tseen[i][slot[i]] = 1
    if tmis:
        return None, None, {'mis': tmis}
    for i in range(len(tnorms)):
        if len(tseen[i]) == 1:
            tail_states[i] = rw(next(iter(tseen[i])), full_bases)
    for b, pg in pages.items():
        pg['tail_slot'] = {i: rw(v, full_bases) for i, v in pg['tail_slot_raw'].items()
                           if tail_states[i] is None and v}
        pg['tail_extra'] = {g: rw('\n'.join(v), full_bases) for g, v in pg['tail_extra_raw'].items() if v}

    # verify the shared footer markup is identical on every page
    for b, pg in pages.items():
        if _ws(strip_current(rw(pg['footer'], full_bases))) != _ws(footer_shared):
            info['footer_diff'].append(b)

    # per-page menu "current" tokens baked into the original markup (needed
    # for cases only the WP object graph can compute: single-post pages
    # shown under a category item, non-anchor page wrappers, ...)
    li_current = re.compile(CUR_TOKEN_RE)
    li_tag = re.compile(r'<li\b[^>]*>', re.I)
    li_id = re.compile(r'\bid="menu-item-(\d+)"')
    li_cls = re.compile(r'\bclass="([^"]*)"')
    over = {}
    for b, pg in pages.items():
        map_ = {}
        for frag in (pg['header'], pg['footer']):
            for m in li_tag.finditer(frag):
                tag = m.group(0)
                idm = li_id.search(tag)
                clsm = li_cls.search(tag)
                if not idm or not clsm:
                    continue
                tokens = [t for t in clsm.group(1).split() if CUR_TOKEN_RE.match(t)]
                if tokens:
                    map_[idm.group(1)] = ' '.join(tokens)
        if map_:
            pg['li_overrides'] = map_

    info['head_norms'] = len(common_norms)
    info['tail_norms'] = len(tnorms)
    info['head_dyn'] = sum(1 for v in head_states if v is None)
    info['tail_dyn'] = sum(1 for v in tail_states if v is None)
    info['head_gaps'] = sorted(set(g for pg in pages.values() for g in pg.get('head_extra', {})))
    info['tail_gaps'] = sorted(set(g for pg in pages.values() for g in pg.get('tail_extra', {})))
    return head_states, tail_states, info