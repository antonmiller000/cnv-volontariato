#!/usr/bin/env python3
"""Regenerate the English story accordion + intro inside trail-angels-website.html
from stories/en.json, so the JSON stays the single source of truth."""
import json,re,html
SITE='/Users/antonrubanenko/Desktop/CNV/site'
d=json.load(open(f'{SITE}/stories/en.json',encoding='utf-8'))
e=lambda t: html.escape(t,quote=False)
out=[]
for i,t in enumerate(d['teams']):
    star='⭐ ' if i==0 else ''
    style=' style="border-color:#2D9A47; border-width:2px;"' if i==0 else ''
    meta=''
    if t.get('period'):
        bits=[t['period']]
        if t.get('location'): bits.append(t['location'])
        if t.get('participants'): bits.append(f"{t['participants']} volunteers")
        meta='<div class="team-meta">'+e(' · '.join(bits))+'</div>'
    body=''.join(f'<p>{e(p)}</p>' for p in t['paragraphs'])
    out.append(
      f'      <div class="team-item"{style}>\n'
      f'        <button class="team-toggle" onclick="toggleTeam(this)">\n'
      f'          <span class="team-label">{star}{e(t["kicker"])} · {e(t["title"])}{meta}</span>\n'
      f'          <span class="team-arrow">▾</span>\n'
      f'        </button>\n'
      f'        <div class="team-body">{body}</div>\n'
      f'      </div>\n')
block='\n'.join(out)

p=f'{SITE}/trail-angels-website.html'; s=open(p,encoding='utf-8').read()
s=re.sub(r'(<div id="blog-teams">\n).*?(\n    </div>\s*\n  </div>\s*\n</div>)',
         lambda m: m.group(1)+block+m.group(2), s, count=1, flags=re.S)
s=re.sub(r'(<p id="ta-intro"[^>]*>).*?(</p>)',
         lambda m: m.group(1)+e(d['ui']['intro'])+m.group(2), s, count=1, flags=re.S)
open(p,'w',encoding='utf-8').write(s)
print('static markup regenerated:', len(d['teams']), 'entries')
