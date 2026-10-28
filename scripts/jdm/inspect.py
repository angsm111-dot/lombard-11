"""Read-only SSH discovery; needs no deployment directory or webserver configuration."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
config=json.loads((ROOT/'hosting/jdm.json').read_text())
# The public host key must be pinned explicitly before any password is sent.
expected=config.get('ssh_host_fingerprint_sha256')
if not expected: raise SystemExit('Awaiting explicit SSH host-key confirmation; password was not sent.')
with tempfile.TemporaryDirectory() as temp:
    known=Path(temp)/'known_hosts';known.write_text(os.environ['JDM_SSH_KNOWN_HOSTS'].strip()+'\n');known.chmod(0o600)
    result=subprocess.run(['ssh-keygen','-lf',str(known),'-E','sha256'],capture_output=True,text=True,check=True)
    values=[line.split()[1] for line in result.stdout.splitlines()]
    if not values or any(value!=expected for value in values): raise SystemExit('SSH fingerprint mismatch; password was not sent.')
    env=os.environ.copy();env['SSHPASS']=env['JDM_SSH_PASSWORD']
    # No wp-config contents, DB access, writes, package installs or site changes.
    command='''set -eu
printf 'ACCOUNT_DIRECTORY='; pwd -P
printf 'PYTHON3='; command -v python3 || true
printf 'PHP='; command -v php || true
printf 'SCP='; command -v scp || true
if test -d public_html; then
  printf 'DOCUMENT_ROOT_CANDIDATE='; realpath public_html
  for item in wp-config.php wp-admin wp-content index.php index.html; do
    if test -e "public_html/$item"; then printf 'PRESENT=%s\\n' "$item"; fi
  done
fi
'''
    args=['sshpass','-e','ssh','-p',str(config['ssh_port']),'-o','BatchMode=no','-o','PreferredAuthentications=password','-o','PubkeyAuthentication=no','-o','NumberOfPasswordPrompts=1','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(known),'-o','ConnectTimeout=20',config['ssh_user']+'@'+config['ssh_host'],'bash -s']
    completed=subprocess.run(args,input=command,text=True,capture_output=True,env=env)
    if completed.returncode: raise SystemExit('Read-only SSH inspection failed; no site files were changed.')
    # Paths are intentionally only in authenticated Actions logs, not the public status branch.
    print(completed.stdout)
