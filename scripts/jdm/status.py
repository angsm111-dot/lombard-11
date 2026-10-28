"""Publish non-secret deployment evidence on jdm-status with normal fast-forward Git."""
import base64, json, os, subprocess, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run(*args,**kw): return subprocess.run(['git',*args],check=True,capture_output=True,text=True,**kw)
source=ROOT/'build/jdm-status.json'
data=json.loads(source.read_text()) if source.exists() else {'project':'lombard-11','state':'failed','phase':'build-or-configuration','commit':os.environ['GITHUB_SHA']}
data.update(run_id=os.environ['GITHUB_RUN_ID'],run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],workflow_result=os.environ.get('WORKFLOW_RESULT','unknown'),recorded_at=datetime.now(timezone.utc).isoformat(),run_url=f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{os.environ["GITHUB_RUN_ID"]}')
if os.environ.get('WORKFLOW_RESULT')!='success':
    data['state']='failed'
    data['public_verified']=False
if source.exists():
    disabled=data.get('disabled_targets',[])
    if disabled and data['state']!='failed':
        data['state']='awaiting_configuration'
        data['public_verified']=False
# Detailed stderr is in the run log, not in the public status branch.
if 'error' in data: data['error']='Operation failed; inspect the phase and linked Actions run.'
env=os.environ.copy();env.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0='AUTHORIZATION: basic '+base64.b64encode(('x-access-token:'+os.environ['GH_STATUS_TOKEN']).encode()).decode())
with tempfile.TemporaryDirectory() as tmp:
    cwd=Path(tmp)
    def git(*args): return run(*args,cwd=cwd,env=env)
    git('init','-q');git('remote','add','origin',f'https://github.com/{os.environ["GITHUB_REPOSITORY"]}.git')
    git('config','user.name','github-actions[bot]');git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
    probe=subprocess.run(['git','ls-remote','--exit-code','origin','refs/heads/jdm-status'],cwd=cwd,env=env,capture_output=True,text=True)
    if probe.returncode==0:
        git('fetch','--depth=1','origin','jdm-status');git('checkout','-B','jdm-status','FETCH_HEAD')
    elif probe.returncode==2: git('checkout','--orphan','jdm-status')
    else: raise RuntimeError('Cannot read status branch; check GitHub permissions')
    (cwd/'runs').mkdir(exist_ok=True)
    (cwd/'latest.json').write_text(json.dumps(data,indent=2)+'\n')
    (cwd/'runs'/f'{data["run_id"]}-{data["run_attempt"]}.json').write_text(json.dumps(data,indent=2)+'\n')
    for file in (ROOT/'build').glob('jdm-*.json'):
        if file.name=='jdm-status.json': continue
        value=json.loads(file.read_text());value.pop('error',None)
        (cwd/file.name).write_text(json.dumps(value,indent=2)+'\n')
    git('add','.');git('commit','-m',f'JDM {data["state"]}: {data["commit"]} [skip ci]');git('push','origin','HEAD:refs/heads/jdm-status')
print('Deployment status saved on jdm-status; state:',data['state'])
