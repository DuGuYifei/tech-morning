"""Validate already-authored HTML; this never generates articles or pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json, re
ROOT = Path(__file__).resolve().parents[1]
class Scan(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=[]; self.refs=[]; self.lang=None; self.h1=0; self.title=False; self.viewport=False; self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='html':self.lang=a.get('lang')
  if tag=='h1':self.h1+=1
  if tag=='title':self.title=True
  if tag=='meta' and a.get('name')=='viewport':self.viewport=True
  if tag=='img':self.images.append(a)
  for key in ('href','src'):
   if key in a:self.refs.append(a[key])
errors=[]; pages={}
for f in ROOT.glob('*.html'):
 if f.name.startswith('qa-'):continue
 p=Scan();p.feed(f.read_text());pages[f.name]=p
 if p.lang!='zh-CN':errors.append(f'{f.name}: missing zh-CN')
 if p.h1!=1:errors.append(f'{f.name}: requires one h1, got {p.h1}')
 if not(p.title and p.viewport):errors.append(f'{f.name}: title/viewport missing')
 if any(n>1 for n in Counter(p.ids).values()):errors.append(f'{f.name}: duplicate IDs')
 for img in p.images:
  if not img.get('alt'):errors.append(f'{f.name}: missing image alt')
 if re.search(r'\bTODO\b|待补|占位|placeholder',f.read_text(),re.I):errors.append(f'{f.name}: unfinished placeholder')
for name,p in pages.items():
 for ref in p.refs:
  u=urlsplit(ref)
  if u.scheme or u.netloc:continue
  target=unquote(u.path) or name
  if not (ROOT/target).exists():errors.append(f'{name}: missing {ref}')
  if u.fragment and target in pages and u.fragment not in pages[target].ids:errors.append(f'{name}: missing anchor {ref}')
issues=json.loads((ROOT/'issues.json').read_text())
assert isinstance(issues,list)
for issue in issues:
 if not (ROOT/issue['path']).is_file():errors.append(f"missing issue {issue['path']}")
if issues and (ROOT/'index.html').read_bytes()!=(ROOT/issues[0]['path']).read_bytes():errors.append('latest index and archive issue differ')
if errors:
 print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(pages)} HTML pages, {len(issues)} issues; local refs, anchors, image alt, language, heading, viewport and latest/archive parity.')
