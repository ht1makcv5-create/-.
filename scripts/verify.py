"""Check all generated routes and assets before publishing; Python standard library only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
problems=[]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set();self.refs=[];self.h1=0;self.title=0;self.description=False
    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if 'id' in a:
            if a['id'] in self.ids: problems.append(f'Duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.title+=1
        if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
        if tag=='img' and 'alt' not in a:problems.append('Image without alt')
        if tag in ['img','script'] and a.get('src'):self.refs.append(a['src'])
        if tag in ['a','link'] and a.get('href'):self.refs.append(a['href'])
        if 'srcset' in a:self.refs.extend(x.strip().split()[0] for x in a['srcset'].split(','))

pages={}
for path in OUT.rglob('*.html'):
    text=path.read_text();doc=Page();doc.feed(text);pages[path]=doc
    if doc.h1!=1 or doc.title!=1 or not doc.description:problems.append(f'Invalid page metadata/headings: {path.relative_to(OUT)}')
    if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}',text):problems.append('Credential-shaped text in rendered output')
for path,doc in pages.items():
    for ref in doc.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if target.is_dir():target=target/'index.html'
        if not target.is_relative_to(OUT.resolve()) or not target.exists():problems.append(f'{path.relative_to(OUT)} → missing {ref}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:problems.append(f'{path.relative_to(OUT)} → missing anchor {ref}')
for name in ['site','guide']:json.loads((ROOT/f'content/{name}.json').read_text())
if problems:
    print('\n'.join(problems));raise SystemExit(1)
print(f'PASS: {len(pages)} HTML pages, internal links, local image variants, anchors, headings and metadata.')
