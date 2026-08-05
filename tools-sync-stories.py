#!/usr/bin/env python3
"""stories/<lang>.json  ->  stories/<lang>.js  + stories/available.js"""
import json, glob, os
SITE='/Users/antonrubanenko/Desktop/CNV/site'; D=os.path.join(SITE,'stories')
langs=[]
for p in sorted(glob.glob(os.path.join(D,'*.json'))):
    d=json.load(open(p,encoding='utf-8'))
    lang=d['lang']; langs.append(lang)
    body=json.dumps(d,ensure_ascii=False,separators=(',',':'))
    open(os.path.join(D,lang+'.js'),'w',encoding='utf-8').write('TA_REGISTER('+body+');\n')
    print(f'  stories/{lang}.js  {len(body)//1024} KB  ({d.get("endonym",lang)})')
# Coherence gate: only offer a language whose structure matches the English source,
# so the site can never show a language with a different set of teams. EACEA review
# explicitly asked for coherent numbering and full project coverage.
en=json.load(open(os.path.join(D,'en.json'),encoding='utf-8'))
ref=[(t.get('year'),t.get('team')) for t in en['teams']]
ok, held = [], []
for l in langs:
    d=json.load(open(os.path.join(D,l+'.json'),encoding='utf-8'))
    sig=[(t.get('year'),t.get('team')) for t in d['teams']]
    (ok if sig==ref else held).append(l)
order=['bg','es','cs','da','de','et','el','en','fr','ga','hr','it','lv','lt','hu','mt','nl','pl','pt','ro','sk','sl','fi','sv']
pub=[l for l in order if l in ok]
open(os.path.join(D,'available.js'),'w',encoding='utf-8').write(
    'window.TA_AVAILABLE='+json.dumps(pub)+';\n')
print(f'  stories/available.js -> {len(pub)}/24 published: {", ".join(pub)}')
if held:
    print(f'  HELD BACK (structure differs from en.json): {", ".join(sorted(held))}')
