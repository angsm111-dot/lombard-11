"""Runner orchestration: full SCP archive, remote hashes, atomic switch, public checks."""
import argparse, base64, hashlib, json, os, re, subprocess, tempfile, time
from pathlib import Path
from urllib.parse import urlsplit
from package import make
ROOT=Path(__file__).resolve().parents[2]
STATUS=ROOT/'build/jdm-status.json'
def record(**values):
    data=json.loads(STATUS.read_text()) if STATUS.exists() else {'project':'lombard-11','commit':os.environ.get('GITHUB_SHA'),'checks':[]}
    data.update(values);STATUS.parent.mkdir(exist_ok=True);STATUS.write_text(json.dumps(data,indent=2)+'\n')
def public_check(url,commit,target,maintenance):
    # curl keeps normal TLS validation and proxy trust. Never use -k.
    stamp=f'{time.time_ns()}'
    def fetch(path):
        with tempfile.TemporaryDirectory() as tmp:
            body=Path(tmp)/'body'
            result=subprocess.run(['curl','--silent','--show-error','--max-time','30','--proto','=https','--header','Cache-Control: no-cache','--output',str(body),'--write-out','%{http_code}',url+path+'?deployment='+stamp],text=True,capture_output=True,check=True)
            return int(result.stdout),body.read_text()
    error=None
    for attempt in range(6):
        try:
            code,text=fetch('/deployment.json');version=json.loads(text)
            if code!=200 or version.get('commit')!=commit or version.get('target')!=target or version.get('project')!='lombard-11': raise ValueError('Public commit marker does not match')
            paths=['/','/kontakt/','/blog/','/oferta/']
            for path in paths:
                code,text=fetch(path)
                if code!=(503 if maintenance else 200): raise ValueError('Public HTTP status does not match expected maintenance state')
                if f'name="deployment-commit" content="{commit}"' not in text: raise ValueError('Public HTML is stale or from another release')
                if maintenance and 'data-maintenance="lombard-11"' not in text: raise ValueError('Maintenance page missing')
                if not maintenance and 'data-maintenance="lombard-11"' in text: raise ValueError('Full version hidden unexpectedly')
                if target=='preview' and 'name="robots" content="noindex' not in text: raise ValueError('Preview noindex missing')
            if not maintenance:
                missing_code,missing_text=fetch('/__lombard11_missing_page__')
                if missing_code!=404: raise ValueError('Unknown URL must return HTTP 404')
            return {'public_verified':True,'observed_commit':commit,'maintenance':maintenance}
        except (ValueError,subprocess.CalledProcessError) as exc:
            error=exc
            if attempt<5: time.sleep(5)
    raise ValueError('Public verification failed: '+str(error))

def run(target,operation):
    config=json.loads((ROOT/'hosting/jdm.json').read_text());commit=os.environ['GITHUB_SHA']
    if not config['paths_verified_from_panel'] or not config['webserver_rules_verified']: raise ValueError('Panel paths and webserver rules have not been verified')
    root=config[target+'_root'];url=config[target+'_url']
    if not root or not url or not config['ssh_host_fingerprint_sha256']: raise ValueError('Confirmed target configuration incomplete')
    parts=urlsplit(url)
    if parts.scheme!='https' or parts.username or parts.path not in ('','/') or parts.query or parts.fragment: raise ValueError('Expected HTTPS root URL')
    if target=='production' and url!='https://lombard11.pl': raise ValueError('Wrong production domain')
    if target=='preview' and parts.hostname in ('lombard11.pl','www.lombard11.pl'): raise ValueError('Preview must be isolated')
    if config['preview_root'] and config['production_root']:
        prod=Path(config['production_root']);preview=Path(config['preview_root'])
        if prod==preview or prod in preview.parents or preview in prod.parents: raise ValueError('Target directories overlap')
    host=os.environ.get('JDM_SSH_HOST','');user=os.environ.get('JDM_SSH_USER','');port=os.environ.get('JDM_SSH_PORT','')
    if not re.fullmatch(r'[a-zA-Z0-9.-]+',host) or not re.fullmatch(r'[a-zA-Z0-9_-]+',user) or not port.isdigit() or not 1<=int(port)<=65535: raise ValueError('SSH host/user/port missing or invalid')
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+',root) or '..' in root.split('/'): raise ValueError('Unsafe deployment root')
    run_id=os.environ['GITHUB_RUN_ID'];attempt=os.environ['GITHUB_RUN_ATTEMPT'];release_id=f'{commit}-{run_id}-{attempt}'
    if not re.fullmatch(r'[0-9a-f]{40}-[0-9]+-[0-9]+',release_id): raise ValueError('Invalid release identity')
    record(state='running',phase='ssh-preflight',target=target,operation=operation)
    with tempfile.TemporaryDirectory() as tmp:
        key=Path(tmp)/'key';known=Path(tmp)/'known_hosts'
        key.write_text(os.environ.get('JDM_SSH_PRIVATE_KEY','').strip()+'\n');key.chmod(0o600)
        known.write_text(os.environ.get('JDM_SSH_KNOWN_HOSTS','').strip()+'\n');known.chmod(0o600)
        fingerprints=subprocess.run(['ssh-keygen','-lf',str(known),'-E','sha256'],capture_output=True,text=True,check=True).stdout
        expected=config['ssh_host_fingerprint_sha256']
        observed=[line.split()[1] for line in fingerprints.splitlines()]
        if not observed or any(value!=expected for value in observed): raise ValueError('Pinned SSH host fingerprint mismatch')
        options=['-o','StrictHostKeyChecking=yes','-o',f'UserKnownHostsFile={known}','-o','ConnectTimeout=20','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3']
        prefix=[]
        if os.environ.get('JDM_SSH_PRIVATE_KEY'):
            options += ['-i',str(key),'-o','IdentitiesOnly=yes','-o','BatchMode=yes']
        elif os.environ.get('JDM_SSH_PASSWORD'):
            os.environ['SSHPASS']=os.environ['JDM_SSH_PASSWORD']
            prefix=['sshpass','-e']
            options += ['-o','BatchMode=no','-o','PreferredAuthentications=password','-o','PubkeyAuthentication=no','-o','NumberOfPasswordPrompts=1']
        else: raise ValueError('Set a dedicated SSH private key or SSH password secret')
        address=f'{user}@{host}'
        def remote(action,**kwargs):
            request={'action':action,'target':target,'root':root,'release_id':release_id,'commit':commit,**kwargs}
            encoded=base64.urlsafe_b64encode(json.dumps(request).encode()).decode()
            result=subprocess.run([*prefix,'ssh',*options,'-p',port,address,'python3 - '+encoded],input=(ROOT/'scripts/jdm/remote.py').read_text(),text=True,capture_output=True)
            if result.returncode: raise ValueError('JDM remote operation failed: '+result.stderr[-1200:])
            return json.loads(result.stdout)
        state=remote('prepare')
        if operation!='deploy':
            state=remote(operation)
            checked=public_check(url,state['commit'],target,state['maintenance'])
            record(state='verified',phase='complete',**checked);return
        output=ROOT/'build'/target
        make(output,target,commit,root)
        digest=(output/'archive.sha256').read_text().strip()
        record(phase='full-scp-transfer',archive_sha256=digest)
        # -O uses the portable SCP protocol; no rsync or incremental sync.
        subprocess.run([*prefix,'scp','-O',*options,'-P',port,str(output/'release.tar.gz'),f'{address}:{root}/incoming/{release_id}.tar.gz'],check=True)
        record(phase='remote-sha256-and-activation')
        published=remote('publish',archive_sha256=digest)
        record(phase='public-verification',remote_verified_files=published['verified_files'])
        try:
            checked=public_check(url,commit,target,published['maintenance'])
        except Exception:
            try:
                result=remote('rollback',previous=published['previous']);record(rollback=result)
            except Exception: record(rollback={'rolled_back':False,'manual_review_required':True})
            raise
        record(state='verified',phase='complete',**checked)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',choices=['production','preview'],required=True);p.add_argument('--operation',choices=['deploy','maintenance-on','maintenance-off'],default='deploy');a=p.parse_args()
    try: run(a.target,a.operation)
    except Exception as exc:
        record(state='failed',error=str(exc));raise
