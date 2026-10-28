"""Create complete release archive with a manifest; never modify source dist/."""
import argparse, hashlib, json, re, shutil, tarfile
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]
def make(output, target, commit, deploy_root, bridge=False):
    if not re.fullmatch(r'[0-9a-f]{40}',commit): raise ValueError('Full commit SHA required')
    if target not in ('production','preview'): raise ValueError('Unknown target')
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+',deploy_root) or '..' in deploy_root.split('/'): raise ValueError('Invalid confirmed deployment root')
    output.mkdir(parents=True,exist_ok=True)
    site=output/'site'
    if site.exists(): raise ValueError('Build directory must be fresh')
    shutil.copytree(ROOT/'dist',site)
    shutil.copyfile(ROOT/'hosting/maintenance.html',site/'maintenance.html')
    # JDM uses Nginx, which ignores .htaccess. Routing is installed separately by JDM.
    nginx=(ROOT/'hosting'/('nginx-'+target+'.conf.example')).read_text()
    (output/'nginx.conf').write_text(nginx.replace('__CONFIRMED_ROOT__',deploy_root))
    if target=='preview': (site/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    if bridge:
        routes={}
        for page in site.rglob('index.html'):
            relative=page.relative_to(site).as_posix()
            route='/'+relative.removesuffix('index.html')
            routes[route]=relative
            if route!='/': routes[route.rstrip('/')]=relative
        (site/'routes.json').write_text(json.dumps(routes,sort_keys=True)+'\n')
    for page in site.rglob('*.html'):
        source=page.read_text().replace('</head>',f'<meta name="deployment-commit" content="{commit}"><meta name="deployment-target" content="{target}"></head>')
        if target=='preview': source=source.replace('</head>','<meta name="robots" content="noindex,nofollow,noarchive"></head>')
        if bridge:
            if target=='preview':
                source=source.replace('href="/','href="/podglad-sezam11/').replace('src="/','src="/podglad-sezam11/')
            else:
                source=source.replace('src="/','src="/sezam11-static/')
                for asset in ('style.css','assets/'):
                    source=source.replace('href="/'+asset,'href="/sezam11-static/'+asset)
        # Version assets so browser/CDN caches cannot hide subsequent updates.
        source=re.sub(r'(src|href)="(/[^"?]+\.(?:css|js|png|webp|jpg|jpeg|svg))"',lambda m:m[1]+'="'+m[2]+'?v='+commit+'"',source)
        page.write_text(source)
    if bridge:
        prefix='/podglad-sezam11' if target=='preview' else '/sezam11-static'
        price=site/'prices.js';price.write_text(price.read_text().replace("fetch('/data/", "fetch('"+prefix+"/data/"))
        if target=='preview':
            app=site/'app.js';source=app.read_text().replace("location.pathname === '/'","location.pathname === '/podglad-sezam11/'")
            source=re.sub(r"(['\"])/([a-z-]+/)(['\"])",lambda m:m[1]+'/podglad-sezam11/'+m[2]+m[3],source)
            app.write_text(source)
    (site/'deployment.json').write_text(json.dumps({'project':'lombard-11','commit':commit,'target':target,'built_at':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
    manifest={p.relative_to(site).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(site.rglob('*')) if p.is_file()}
    (site/'SHA256SUMS.json').write_text(json.dumps(manifest,sort_keys=True)+'\n')
    archive=output/'release.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for p in sorted(site.rglob('*')):
            if p.is_file(): tar.add(p,arcname=p.relative_to(site).as_posix(),recursive=False)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/'archive.sha256').write_text(digest+'\n')
    print(f'Packaged {len(manifest)} files, SHA-256 {digest}')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--target',choices=['production','preview'],required=True);p.add_argument('--commit',required=True);p.add_argument('--root',required=True);a=p.parse_args();make(a.output,a.target,a.commit,a.root)
