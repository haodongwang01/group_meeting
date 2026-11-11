"""Check routes, anchors, assets, content and metadata without dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,sys
root=Path(__file__).resolve().parent.parent; dist=root/'dist'; errors=[]
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.links=[];self.images=[];self.h1=0;self.description=False;self.title=False;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='title':self.title=True
  if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
  if tag in ['a','link','script','img']:
   v=a.get('href') or a.get('src')
   if v:self.links.append(v)
  if tag=='img' and a.get('src'):self.images.append(a)
pages={p:Page(p.read_text(encoding='utf-8')) for p in dist.rglob('*.html')}
for p,doc in pages.items():
 if doc.h1!=1:errors.append(f'{p.name}: expected one h1')
 if not doc.description or not doc.title:errors.append(f'{p.name}: missing metadata')
 if len(doc.ids)!=len(set(doc.ids)):errors.append(f'{p.name}: duplicate IDs')
 for a in doc.images:
  if 'alt' not in a:errors.append(f'{p.name}: missing image alt')
 for href in doc.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  target=(dist/unquote(u.path).lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(f'{p.name}: missing {href}')
  elif u.fragment and target.suffix=='.html':
   other=pages.get(target) or Page(target.read_text(encoding='utf-8'))
   if unquote(u.fragment) not in other.ids:errors.append(f'{p.name}: broken anchor {href}')
for m in json.loads((root/'content/meetings.json').read_text(encoding='utf-8')):
 content=(root/'content'/f"{m['date']}.html").read_text(encoding='utf-8')
 page=(dist/'meetings'/f"{m['date']}.html").read_text(encoding='utf-8')
 if content not in page:errors.append(f"{m['date']}: incomplete body")
for p in dist.rglob('*'):
 if p.suffix.lower() in ['.pdf','.docx','.tex','.pptx']:errors.append(f'Original document exposed: {p}')
print(json.dumps({'pages':len(pages),'images':len(list((dist/'assets/images').glob('*'))),'errors':errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
