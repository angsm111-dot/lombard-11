"""Validate generated pages and local assets, without network or credentials."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib, json
ROOT = Path(__file__).resolve().parents[2]
def check(root):
    errors=[]
    class Page(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a=dict(attrs)
            for key in ('href','src'):
                url=a.get(key,''); parts=urlsplit(url)
                if parts.scheme or parts.netloc or not parts.path: continue
                dest=(root / unquote(parts.path).lstrip('/')) if parts.path.startswith('/') else current.parent / unquote(parts.path)
                if dest.is_dir(): dest=dest/'index.html'
                if not dest.is_file(): errors.append(f'{current.relative_to(root)}: missing {url}')
    for current in root.rglob('*.html'):
        source=current.read_text()
        if '<title>' not in source or 'lang="pl"' not in source: errors.append(f'Invalid page: {current}')
        Page().feed(source)
    posts=json.loads((root/'data/articles.json').read_text())
    hashes=[hashlib.sha256((root/p['image'].lstrip('/')).read_bytes()).hexdigest() for p in posts]
    if len(hashes)!=len(set(hashes)): errors.append('Blog photographs repeat')
    if errors: raise SystemExit('\n'.join(errors))
    print(f'Validated {len(list(root.rglob("*.html")))} pages and {len(posts)} distinct blog photos.')
if __name__=='__main__': check(ROOT/'dist')
