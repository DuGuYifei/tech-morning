"""Read-only deployment check: compare public static assets with local bytes."""
from pathlib import Path
from urllib.request import Request, urlopen
from hashlib import sha256
import sys
root=Path(__file__).resolve().parents[1]
base=(sys.argv[1] if len(sys.argv)>1 else 'https://about.liuyifei.tech/tech-morning/').rstrip('/')+'/'
paths=[p for p in root.glob('*.html') if not p.name.startswith('qa-')]+list((root/'assets').glob('*'))+[root/'issues.json']
failed=[]
for p in paths:
 relative=p.relative_to(root).as_posix()
 try:
  with urlopen(Request(base+relative,headers={'Cache-Control':'no-cache'}),timeout=30) as r:
   actual=r.read(); expected=p.read_bytes();ok=r.status==200 and sha256(actual).digest()==sha256(expected).digest()
   print(('PASS' if ok else 'MISMATCH'),relative,r.status,r.url)
   if not ok:failed.append(relative)
 except Exception as e:failed.append(relative);print('ERROR',relative,str(e))
if failed:raise SystemExit(1)
print('PASS: all public content matches local bytes. Browser visual/navigation QA is separate.')
