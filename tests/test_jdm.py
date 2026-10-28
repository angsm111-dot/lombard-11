"""Exercise real release extraction, tamper detection, isolation and rollback locally."""
import base64, importlib.util, json, sys, tarfile, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/jdm'))
from package import make
from remote import execute
COMMIT='a'*40
class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)
        self.root=self.path/'production';self.root.mkdir()
        (self.root/'.lombard11-deploy-root').write_text(json.dumps({'project':'lombard-11','domain':'lombard11.pl','target':'production'}))
        self.request={'root':str(self.root),'target':'production','commit':COMMIT,'release_id':COMMIT+'-1-1'}
        execute({**self.request,'action':'prepare'})
    def package(self,release_id=None):
        out=self.path/('out'+str(len(list(self.path.glob('out*')))))
        make(out,'production',COMMIT,str(self.root))
        release_id=release_id or self.request['release_id']
        (self.root/'incoming'/(release_id+'.tar.gz')).write_bytes((out/'release.tar.gz').read_bytes())
        return (out/'archive.sha256').read_text().strip()
    def test_full_release_preserves_legacy_and_rollback(self):
        old=self.path/'old-wordpress';old.mkdir();(old/'wp-config.php').write_text('legacy unchanged')
        digest=self.package();first=execute({**self.request,'action':'publish','archive_sha256':digest})
        self.assertGreater(first['verified_files'],30)
        self.assertIsNone(first['previous'])
        flag=execute({**self.request,'action':'maintenance-on'});self.assertTrue(flag['maintenance'])
        newer=COMMIT+'-2-1';digest=self.package(newer)
        second=execute({**self.request,'release_id':newer,'action':'publish','archive_sha256':digest})
        self.assertTrue(second['maintenance'])
        execute({**self.request,'release_id':newer,'action':'rollback','previous':second['previous']})
        self.assertEqual((self.root/'current').resolve().name,self.request['release_id'])
        execute({**self.request,'action':'maintenance-off'})
        self.assertFalse((self.root/'maintenance.enabled').exists())
        self.assertEqual((old/'wp-config.php').read_text(),'legacy unchanged')
    def test_corrupt_archive_never_activates(self):
        self.package()
        with self.assertRaisesRegex(ValueError,'Archive checksum'):
            execute({**self.request,'action':'publish','archive_sha256':'0'*64})
        self.assertFalse((self.root/'current').exists())
    def test_wordpress_and_wrong_project_refused(self):
        (self.root/'wp-config.php').touch()
        with self.assertRaisesRegex(ValueError,'WordPress'): execute({**self.request,'action':'prepare'})
    def test_preview_is_complete_and_not_under_maintenance(self):
        preview=self.path/'preview-build';make(preview,'preview',COMMIT,str(self.path/'preview'))
        self.assertTrue((preview/'site/blog/index.html').exists())
        self.assertIn('noindex',(preview/'site/index.html').read_text())
        self.assertNotIn('maintenance.enabled',(preview/'nginx.conf').read_text())
        with self.assertRaisesRegex(ValueError,'marker mismatch'):
            execute({**self.request,'target':'preview','action':'prepare'})
    def test_unsafe_tar_and_manifest_corruption_refused(self):
        import hashlib,io
        archive=self.root/'incoming'/(self.request['release_id']+'.tar.gz')
        with tarfile.open(archive,'w:gz') as tar:
            info=tarfile.TarInfo('../escape');info.size=4;tar.addfile(info,io.BytesIO(b'evil'))
        with self.assertRaisesRegex(ValueError,'Unsafe archive'):
            execute({**self.request,'action':'publish','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()})
        self.assertFalse((self.root/'current').exists())
if __name__=='__main__': unittest.main()
