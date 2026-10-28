"""Deploy through existing PHP/Nginx without moving or deleting WordPress."""
import base64, hashlib, json, os, re, secrets, subprocess, tempfile, time
from pathlib import Path
from package import make
from deploy import ROOT, record, public_check

def run(target,operation):
    if operation!='deploy': raise ValueError('SSL and maintenance setup deferred by owner; deploy only')
    config=json.loads((ROOT/'hosting/jdm.json').read_text());commit=os.environ['GITHUB_SHA']
    doc=config['document_root'];root=config[target+'_root'];url=config[target+'_url']
    if target not in ('preview','production') or doc!='/home/lombardp/public_html' or root!='/home/lombardp/.sezam11-'+target: raise ValueError('Unexpected account paths')
    release_id=commit+'-'+os.environ['GITHUB_RUN_ID']+'-'+os.environ['GITHUB_RUN_ATTEMPT']
    if not re.fullmatch(r'[0-9a-f]{40}-[0-9]+-[0-9]+',release_id): raise ValueError('Invalid release identifier')
    record(state='running',phase='php-ssh-preflight',target=target,operation=operation)
    with tempfile.TemporaryDirectory() as temp:
        known=Path(temp)/'known_hosts';known.write_text((os.environ.get('JDM_SSH_KNOWN_HOSTS') or (ROOT/'hosting/ssh_known_hosts').read_text()).strip()+'\n');known.chmod(0o600)
        lines=subprocess.run(['ssh-keygen','-lf',str(known),'-E','sha256'],text=True,capture_output=True,check=True).stdout.splitlines()
        if not lines or any(line.split()[1]!=config['ssh_host_fingerprint_sha256'] for line in lines): raise ValueError('SSH pin mismatch')
        env=os.environ.copy();env['SSHPASS']=env['JDM_SSH_PASSWORD']
        options=['-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),'-o','PreferredAuthentications=password','-o','PubkeyAuthentication=no','-o','NumberOfPasswordPrompts=1','-o','ConnectTimeout=20','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3']
        address=config['ssh_user']+'@'+config['ssh_host'];port=str(config['ssh_port'])
        def remote(action,**kw):
            q={'document_root':doc,'root':root,'target':target,'commit':commit,'release_id':release_id,'action':action,**kw}
            encoded=base64.urlsafe_b64encode(json.dumps(q).encode()).decode()
            result=subprocess.run(['sshpass','-e','ssh',*options,'-p',port,address,"php -r 'eval(stream_get_contents(STDIN));' "+encoded],input=(ROOT/'scripts/jdm/remote.php').read_text(),capture_output=True,text=True,env=env)
            if result.returncode: raise ValueError('JDM PHP operation failed: '+result.stderr[-1200:])
            return json.loads(result.stdout)
        # Prove actual domain/root binding before creating private deployment directories.
        nonce=secrets.token_hex(32);proof=remote('probe',nonce=nonce)
        if proof.get('existing_standalone'):
            public_check('https://lombard11.pl',proof['commit'],'production',False)
        else:
            result=subprocess.run(['curl','--fail','--silent','--show-error','--max-time','30','--proto','=https','--header','Cache-Control: no-cache','https://lombard11.pl'+proof['proof_path']+'?v='+str(time.time_ns())],capture_output=True,text=True,check=True)
            if result.stdout!=nonce: raise ValueError('Public domain does not match inspected document root')
        record(phase='domain-root-proven',document_root_verified=True)
        remote('prepare')
        output=ROOT/'build'/target;make(output,target,commit,root,bridge=(target=='preview'))
        digest=(output/'archive.sha256').read_text().strip();record(phase='full-scp-transfer',archive_sha256=digest)
        subprocess.run(['sshpass','-e','scp','-O',*options,'-P',port,str(output/'release.tar.gz'),address+':'+root+'/incoming/'+release_id+'.tar.gz'],env=env,check=True)
        published=remote('publish',archive_sha256=digest)
        record(phase='public-verification',remote_verified_files=published['verified_files'])
        static_activated=False
        try:
            if target=='production':
                # Initial public stage lives alongside old WP; later updates are already standalone.
                if not proof.get('existing_standalone'):
                    public_check('https://lombard11.pl/sezam11-stage',commit,target,False,check_missing=False)
                remote('activate-static')
                static_activated=True
            checked=public_check(url,commit,target,False,check_missing=(target=='production'))
            # Check direct CSS and a representative image as Nginx may have separate asset rules.
            prefix='/podglad-sezam11' if target=='preview' else ''
            for asset in ('style.css','app.js','assets/logo.png'):
                response=subprocess.run(['curl','--fail','--silent','--show-error','--max-time','30','--proto','=https','https://lombard11.pl'+prefix+'/'+asset+'?v='+commit],capture_output=True,check=True).stdout
                if hashlib.sha256(response).digest()!=hashlib.sha256((output/'site'/asset).read_bytes()).digest(): raise ValueError('Public asset checksum mismatch')
        except Exception:
            if static_activated and published['previous'] is None: remote('restore-legacy')
            try: record(rollback=remote('rollback',previous=published['previous']))
            except Exception: record(rollback={'rolled_back':False,'manual_review_required':True})
            raise
        record(state='verified',phase='complete',**checked)
