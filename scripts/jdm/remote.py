"""Executed on JDM through pinned SSH. No deletes, no WordPress modifications."""
import base64, fcntl, hashlib, json, os, re, sys, tarfile
from pathlib import Path, PurePosixPath

def root_checked(value,target):
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+',value) or '..' in value.split('/'): raise ValueError('Unsafe root')
    root=Path(value)
    if root.resolve()!=root or str(root) in ('/','/home','/var','/var/www','/tmp'): raise ValueError('Root must be a dedicated real directory')
    marker=root/'.lombard11-deploy-root'
    if json.loads(marker.read_text())!={'project':'lombard-11','domain':'lombard11.pl','target':target}: raise ValueError('Project marker mismatch')
    for name in ('wp-config.php','wp-admin','wp-content','wp-includes','index.php'):
        if (root/name).exists(): raise ValueError('WordPress/legacy content detected: refused')
    for name in ('incoming','releases'):
        path=root/name
        if path.is_symlink(): raise ValueError('Symlink directory refused')
        path.mkdir(exist_ok=True)
    current=root/'current'
    if current.exists() and not current.is_symlink(): raise ValueError('Current is not a release symlink')
    if current.is_symlink() and current.resolve().parent!=root/'releases': raise ValueError('Current points outside release directory')
    return root

def manifest_check(release):
    manifest=json.loads((release/'SHA256SUMS.json').read_text())
    files={p.relative_to(release).as_posix() for p in release.rglob('*') if p.is_file()}
    if files!=set(manifest)|{'SHA256SUMS.json'}: raise ValueError('Manifest file set mismatch')
    for name,digest in manifest.items():
        if hashlib.sha256((release/name).read_bytes()).hexdigest()!=digest: raise ValueError('File checksum mismatch')
    return len(manifest)

def execute(req):
    target=req['target'];root=root_checked(req['root'],target);action=req['action']
    with (root/'.deploy.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if action=='prepare': return {'ready':True,'maintenance':(root/'maintenance.enabled').exists()}
        if action in ('maintenance-on','maintenance-off'):
            if target!='production': raise ValueError('Maintenance is production only')
            if not (root/'current/deployment.json').is_file(): raise ValueError('Deploy a verified release first')
            flag=root/'maintenance.enabled'
            if action=='maintenance-on': flag.touch(exist_ok=True)
            else: flag.unlink(missing_ok=True) # Only the dedicated flag; never website files.
            return {'maintenance':flag.exists(),'commit':json.loads((root/'current/deployment.json').read_text())['commit']}
        release_id=req['release_id']
        if not re.fullmatch(r'[0-9a-f]{40}-[0-9]+-[0-9]+',release_id): raise ValueError('Invalid release id')
        current=root/'current'
        if action=='rollback':
            if not current.is_symlink() or current.resolve()!=root/'releases'/release_id: raise ValueError('Refusing to roll back another release')
            previous=req.get('previous')
            if previous is None: raise ValueError('First release retained for inspection; panel rollback required')
            if not re.fullmatch(r'[0-9a-f]{40}-[0-9]+-[0-9]+',previous): raise ValueError('Invalid previous release')
            dest=root/'releases'/previous;manifest_check(dest)
            tmp=root/('switch-'+release_id)
            tmp.symlink_to('releases/'+previous);os.replace(tmp,current)
            return {'rolled_back':True}
        if action!='publish': raise ValueError('Unsupported operation')
        archive=root/'incoming'/(release_id+'.tar.gz')
        if archive.is_symlink() or hashlib.sha256(archive.read_bytes()).hexdigest()!=req['archive_sha256']: raise ValueError('Archive checksum mismatch')
        dest=root/'releases'/release_id
        dest.mkdir() # Never overwrite an existing release.
        with tarfile.open(archive,'r:gz') as tar:
            members=tar.getmembers();names=set()
            for member in members:
                path=PurePosixPath(member.name)
                if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name in names: raise ValueError('Unsafe archive member')
                names.add(member.name)
            for member in members:
                path=dest/member.name;path.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as source,path.open('xb') as out: out.write(source.read())
                path.chmod(0o644)
        count=manifest_check(dest)
        version=json.loads((dest/'deployment.json').read_text())
        if version['commit']!=req['commit'] or version['target']!=target or version['project']!='lombard-11': raise ValueError('Wrong deployment identity')
        previous=current.resolve().name if current.is_symlink() else None
        tmp=root/('switch-'+release_id);tmp.symlink_to('releases/'+release_id);os.replace(tmp,current)
        return {'published':True,'previous':previous,'verified_files':count,'maintenance':(root/'maintenance.enabled').exists()}
if __name__=='__main__':
    req=json.loads(base64.urlsafe_b64decode(sys.argv[1]));print(json.dumps(execute(req)))
