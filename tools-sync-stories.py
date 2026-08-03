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
order=['bg','es','cs','da','de','et','el','en','fr','ga','hr','it','lv','lt','hu','mt','nl','pl','pt','ro','sk','sl','fi','sv']
langs=[l for l in order if l in langs]
open(os.path.join(D,'available.js'),'w',encoding='utf-8').write(
    'window.TA_AVAILABLE='+json.dumps(langs)+';\n')
print(f'  stories/available.js -> {len(langs)}/24: {", ".join(langs)}')
