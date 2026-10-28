"""Read-only runner audit. Keyscan is evidence, never automatic SSH trust."""
import json, socket, ssl, subprocess, tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
config=json.loads((ROOT/'hosting/jdm.json').read_text())
result={'project':'lombard-11','checked_at':datetime.now(timezone.utc).isoformat(),'origin_tls_verified':False,'cloudflare_ssl_mode_verified':False,'ssh_host_identity_verified':False}
try:
    result['public_addresses']=sorted({a[4][0] for a in socket.getaddrinfo('lombard11.pl',443)})
    with socket.create_connection(('lombard11.pl',443),timeout=15) as connection:
        with ssl.create_default_context().wrap_socket(connection,server_hostname='lombard11.pl') as tls:
            cert=tls.getpeercert()
            result['public_tls']={'verified':True,'issuer':cert.get('issuer'),'subject_alt_names':cert.get('subjectAltName'),'not_after':cert.get('notAfter'),'scope':'public endpoint only; not JDM origin'}
except Exception as exc: result['public_tls']={'verified':False,'error_type':type(exc).__name__}
try:
    keys=subprocess.run(['ssh-keyscan','-T','8','-p',str(config['ssh_port']),'-t','ed25519',config['ssh_host']],capture_output=True,text=True,timeout=20,check=True).stdout
    lines=[line for line in keys.splitlines() if not line.startswith('#')]
    if not lines: raise ValueError('No SSH host key returned')
    with tempfile.NamedTemporaryFile(mode='w+') as file:
        file.write('\n'.join(lines)+'\n');file.flush()
        fingerprints=subprocess.run(['ssh-keygen','-lf',file.name,'-E','sha256'],capture_output=True,text=True,check=True).stdout.splitlines()
    result['ssh_discovery']={'unverified_known_hosts':lines,'unverified_fingerprints':fingerprints,'warning':'Cross-check with JDM before pinning; keyscan does not establish server identity.'}
except Exception as exc: result['ssh_discovery']={'error_type':type(exc).__name__,'verified':False}
(ROOT/'build').mkdir(exist_ok=True)
(ROOT/'build/jdm-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Read-only public audit saved; no SSH authentication or configuration changes.')
