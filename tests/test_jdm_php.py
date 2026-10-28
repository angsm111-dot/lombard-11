"""Exercise the actual PHP transport on CI; no production or network needed."""
import base64,hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts/jdm'))
from package import make
SHA='b'*40
@unittest.skipUnless(shutil.which('php'),'PHP CLI required (installed on CI)')
class PHPTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.account=Path(self.temp.name);self.doc=self.account/'public_html';self.doc.mkdir()
        (self.doc/'wp-config.php').write_text('PRESERVE');(self.doc/'wp-admin').mkdir()
        self.q={'document_root':str(self.doc),'root':str(self.account/'.sezam11-preview'),'target':'preview','commit':SHA,'release_id':SHA+'-1-1'}
    def remote(self,action,success=True,**extra):
        q={**self.q,'action':action,**extra};arg=base64.urlsafe_b64encode(json.dumps(q).encode()).decode()
        result=subprocess.run(['php','-r','eval(stream_get_contents(STDIN));',arg],input=(ROOT/'scripts/jdm/remote.php').read_text(),text=True,capture_output=True)
        if success:self.assertEqual(result.returncode,0,result.stderr);return json.loads(result.stdout)
        self.assertNotEqual(result.returncode,0);return result
    def test_preview_transfer_and_corruption_rejection(self):
        self.remote('probe',nonce='c'*64);self.remote('prepare')
        out=self.account/'build';make(out,'preview',SHA,self.q['root'],bridge=True)
        archive=Path(self.q['root'])/'incoming'/(self.q['release_id']+'.tar.gz');shutil.copyfile(out/'release.tar.gz',archive)
        self.remote('publish',success=False,archive_sha256='0'*64)
        result=self.remote('publish',archive_sha256=(out/'archive.sha256').read_text().strip())
        self.assertGreater(result['verified_files'],30)
        self.assertTrue((self.doc/'podglad-sezam11').is_symlink())
        source=(self.doc/'podglad-sezam11/index.html').read_text()
        self.assertIn('href="/podglad-sezam11/',source)
        self.assertIn('src="/podglad-sezam11/',source)
        self.assertEqual((self.doc/'wp-config.php').read_text(),'PRESERVE')
    def test_standalone_activation_preserves_wordpress_and_rolls_back(self):
        self.q.update(target='production',root=str(self.account/'.sezam11-production'))
        self.remote('prepare');out=self.account/'build';make(out,'production',SHA,self.q['root'])
        shutil.copyfile(out/'release.tar.gz',Path(self.q['root'])/'incoming'/(self.q['release_id']+'.tar.gz'))
        self.remote('publish',archive_sha256=(out/'archive.sha256').read_text().strip())
        result=self.remote('activate-static');self.assertTrue(result['standalone'])
        self.assertTrue(self.doc.is_symlink())
        self.assertIn('/style.css',(self.doc/'index.html').read_text())
        self.assertFalse((self.doc/'wp-config.php').exists())
        self.remote('probe',nonce='c'*64)
        self.remote('restore-legacy')
        self.assertFalse(self.doc.is_symlink())
        self.assertEqual((self.doc/'wp-config.php').read_text(),'PRESERVE')
    def test_maintenance_is_503_and_preview_stays_complete(self):
        prod=self.account/'maintenance-build';make(prod,'production',SHA,str(self.account/'.sezam11-production'),maintenance=True)
        self.assertFalse((prod/'site/index.html').exists())
        self.assertFalse((prod/'site/data/articles.json').exists())
        self.assertTrue((prod/'site/blog/index.php').exists())
        self.assertIn('http_response_code(503)',(prod/'site/index.php').read_text())
        self.assertTrue(json.loads((prod/'site/deployment.json').read_text())['maintenance'])
        preview=self.account/'preview-build';make(preview,'preview',SHA,self.q['root'],bridge=True)
        self.assertTrue((preview/'site/blog/index.html').is_file())
        self.assertFalse(json.loads((preview/'site/deployment.json').read_text())['maintenance'])
        with self.assertRaises(ValueError):make(self.account/'bad','preview',SHA,self.q['root'],maintenance=True)
