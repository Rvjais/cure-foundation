# -*- coding: utf-8 -*-
"""Driver: analyze the HTML mirror and emit the whole PHP tree."""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genmod import analyze, render
from genmod.staticdata import load, base_of

print('== load ==')
pages, stubs, full_bases = load()
stubs = [base_of(p) for p, _ in stubs]
print('pages: %d, stubs: %d' % (len(pages), len(stubs)))

# consistency of the page shell across all pages
dts = set(pg['doctype'] for pg in pages.values())
hts = set(pg['html_tag'] for pg in pages.values())
ens = set(pg['end_html'] for pg in pages.values())
if len(dts) != 1 or len(hts) != 1 or len(ens) != 1:
    print('doctype:', {repr(x[:40]) for x in dts})
    print('html tag:', {repr(x) for x in hts})
    print('end:', {repr(x[:40]) for x in ens})
    sys.exit(1)
print('doctype/html-tag/end consistent on every page')

print('== analyze ==')
head_states, tail_states, info = analyze.analyze(pages, full_bases)
if head_states is None:
    print('alignment problems:', info.get('mis', [])[:10])
    sys.exit(1)
if info['footer_diff']:
    print('shared footer diffs:', info['footer_diff'][:5])
    sys.exit(1)
print('header variants: %d' % len(info['header_variants']))
print('common head elements: %d (dyn %d), gaps %s' % (info['head_norms'], info['head_dyn'], info['head_gaps']))
print('common tail elements: %d (dyn %d), gaps %s' % (info['tail_norms'], info['tail_dyn'], info['tail_gaps']))

ref = pages[''] if '' in pages else pages['about-us']
info['doctype'] = ref['doctype']
info['html_tag'] = ref['html_tag']

print('== emit includes ==')
render.emit_includes(head_states, tail_states, info['header_variants'], info['footer_shared'],
                     ref['doctype'], ref['html_tag'])

routes = render.build_routes(full_bases, stubs)
overrides = {}
for b, pg in pages.items():
    if pg.get('li_overrides'):
        overrides[pg['urlpath']] = {k: v for k, v in sorted(pg['li_overrides'].items())}
print('menu overrides for %d pages' % len(overrides))
render.emit_config(routes, ref['doctype'], ref['html_tag'], ref['end_html'], overrides)
print('routes:', len(routes), '(full pages %d + stub variants)' % sum(1 for v in routes.values() if v.startswith('pages/')))

print('== emit pages ==')
for b, pg in pages.items():
    render.emit_page(b, pg, head_states, tail_states)
for name in stubs:
    render.emit_stub(name)
print('emitted %d page files + %d stubs' % (len(pages), len(stubs)))
print('done')
