/* PHP 7.4+ remote release manager. Receives code via stdin, not a public PHP URL. */
function require_ok($condition,$message) { if (!$condition) { throw new RuntimeException($message); } }
function process_args($args) {
    $pipes=[];$proc=proc_open($args,[1=>['pipe','w'],2=>['pipe','w']],$pipes);
    require_ok(is_resource($proc),'Cannot start required tool');
    $out=stream_get_contents($pipes[1]);$err=stream_get_contents($pipes[2]);fclose($pipes[1]);fclose($pipes[2]);
    require_ok(proc_close($proc)===0,'Remote tool failed');return $out;
}
function safe_root($root) {
    require_ok((bool)preg_match('~^/[A-Za-z0-9_./-]+$~D',$root) && !in_array('..',explode('/',$root),true),'Invalid root');
    return $root;
}
function verify_release($dir) {
    $manifest=json_decode(file_get_contents($dir.'/SHA256SUMS.json'),true,512,JSON_THROW_ON_ERROR);$files=[];
    $iterator=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir,FilesystemIterator::SKIP_DOTS));
    foreach ($iterator as $path) {
        if ($path->isLink()) {
            require_ok(basename($path->getPathname())==='podglad-sezam11' && readlink($path->getPathname())===dirname(dirname(dirname($dir))).'/.sezam11-preview/current','Release contains unexpected link');
            continue;
        }
        if ($path->isFile()) { $name=substr($path->getPathname(),strlen($dir)+1);$files[]=$name; }
    }
    $expected=array_merge(array_keys($manifest),['SHA256SUMS.json']);sort($expected);sort($files);
    require_ok($expected===$files,'Manifest file set mismatch');
    foreach ($manifest as $name=>$hash) { require_ok(hash_equals($hash,hash_file('sha256',$dir.'/'.$name)),'File SHA256 mismatch'); }
    return count($manifest);
}
try {
    $q=json_decode(base64_decode(strtr($argv[1],'-_','+/')),true,512,JSON_THROW_ON_ERROR);
    $doc=safe_root($q['document_root']);$account=dirname($doc);
    $standalone=is_link($doc) && readlink($doc)===$account.'/.sezam11-production/current';
    require_ok(basename($doc)==='public_html' && ($standalone || (realpath($doc)===$doc && is_file($doc.'/wp-config.php') && is_dir($doc.'/wp-admin'))),'Unexpected document root');
    $action=$q['action'];$answer=[];
    if ($action==='probe' && $standalone) {
        $version=json_decode(file_get_contents($doc.'/deployment.json'),true,512,JSON_THROW_ON_ERROR);
        require_ok($version['project']==='lombard-11' && $version['target']==='production','Wrong active site');
        $answer=['existing_standalone'=>true,'commit'=>$version['commit']];
    } elseif ($action==='probe') {
        require_ok((bool)preg_match('/^[a-f0-9]{40}$/D',$q['commit']),'Bad commit');
        require_ok((bool)preg_match('/^[a-f0-9]{64}$/D',$q['nonce']),'Bad proof');
        $path=$doc.'/sezam11-proof-'.$q['commit'].'-'.substr($q['nonce'],0,12).'.txt';
        if (file_exists($path)) { require_ok(file_get_contents($path)===$q['nonce'],'Probe collision'); }
        else { $handle=fopen($path,'x');require_ok($handle!==false,'Cannot create isolated domain proof');fwrite($handle,$q['nonce']);fclose($handle);chmod($path,0644); }
        $answer=['proof_path'=>'/sezam11-proof-'.$q['commit'].'-'.substr($q['nonce'],0,12).'.txt'];
    } else {
        $target=$q['target'];require_ok(in_array($target,['production','preview'],true),'Invalid target');
        $root=safe_root($q['root']);require_ok($root===$account.'/.sezam11-'.$target,'Root must be isolated in the verified account');
        $marker=$root.'/.lombard11-deploy-root';
        if (!file_exists($root)) {
            require_ok($action==='prepare','Prepare first');mkdir($root,0755);
            file_put_contents($marker,json_encode(['project'=>'lombard-11','domain'=>'lombard11.pl','target'=>$target]));
        }
        require_ok(realpath($root)===$root,'Root must not be a symlink');
        $identity=json_decode(file_get_contents($marker),true);
        require_ok($identity==['project'=>'lombard-11','domain'=>'lombard11.pl','target'=>$target],'Project marker mismatch');
        foreach (['incoming','releases'] as $name) { require_ok(!is_link($root.'/'.$name),'Unexpected symlink');if(!is_dir($root.'/'.$name))mkdir($root.'/'.$name,0755); }
        $lock=fopen($root.'/.deploy.lock','a');require_ok(flock($lock,LOCK_EX),'Cannot lock deployment');
        $current=$root.'/current';require_ok(!file_exists($current) || is_link($current),'Current is not a symlink');
        if(is_link($current))require_ok(dirname(realpath($current))===$root.'/releases','Current outside releases');
        if($action==='prepare') { $answer=['ready'=>true]; }
        elseif($action==='publish') {
            $id=$q['release_id'];require_ok((bool)preg_match('/^[a-f0-9]{40}-[0-9]+-[0-9]+$/D',$id),'Invalid release id');
            $archive=$root.'/incoming/'.$id.'.tar.gz';require_ok(!is_link($archive) && hash_equals($q['archive_sha256'],hash_file('sha256',$archive)),'Archive SHA256 mismatch');
            $names=explode("\n",trim(process_args(['tar','-tzf',$archive])));$seen=[];
            foreach($names as $name) {
                require_ok((bool)preg_match('~^[A-Za-z0-9_./-]+$~D',$name) && $name[0]!=='/' && !in_array('..',explode('/',$name),true) && !isset($seen[$name]),'Unsafe archive path');$seen[$name]=true;
            }
            foreach(explode("\n",trim(process_args(['tar','-tvzf',$archive]))) as $line) { require_ok($line[0]==='-','Archive contains non-file'); }
            $dest=$root.'/releases/'.$id;require_ok(!file_exists($dest),'Release already exists');mkdir($dest,0755);
            process_args(['tar','--no-same-owner','--no-same-permissions','-xzf',$archive,'-C',$dest]);
            $count=verify_release($dest);$version=json_decode(file_get_contents($dest.'/deployment.json'),true);
            require_ok($version['project']==='lombard-11' && $version['target']===$target && $version['commit']===$q['commit'],'Wrong deployment identity');
            if($target==='production') {
                require_ok(symlink($account.'/.sezam11-preview/current',$dest.'/podglad-sezam11'),'Cannot attach independent preview');
            }
            $previous=is_link($current)?basename(realpath($current)):null;
            $tmp=$root.'/switch-'.$id;require_ok(!file_exists($tmp) && !is_link($tmp),'Temporary link exists');symlink('releases/'.$id,$tmp);require_ok(rename($tmp,$current),'Cannot activate release');
            $public=$doc.($target==='preview'?'/podglad-sezam11':'/sezam11-stage');
            if($target==='production' && $standalone) $public=null;
            if($public!==null) {
            require_ok((!file_exists($public) && !is_link($public)) || (is_link($public) && readlink($public)===$current),'Public path collision');
            if(!is_link($public))require_ok(symlink($current,$public),'Cannot expose isolated release');
            }
            $answer=['published'=>true,'previous'=>$previous,'verified_files'=>$count];
        } elseif($action==='rollback') {
            require_ok(is_link($current) && basename(realpath($current))===$q['release_id'],'Another release is active');
            $previous=$q['previous'];require_ok(is_string($previous) && (bool)preg_match('/^[a-f0-9]{40}-[0-9]+-[0-9]+$/D',$previous),'No previous release');
            verify_release($root.'/releases/'.$previous);$tmp=$root.'/rollback-'.$q['release_id'];symlink('releases/'.$previous,$tmp);require_ok(rename($tmp,$current),'Cannot rollback');$answer=['rolled_back'=>true];
        } elseif($action==='activate-static') {
            require_ok($target==='production' && is_link($current),'Production release missing');
            verify_release(realpath($current));
            if(!$standalone) {
                $backup=$account.'/.sezam11-wordpress-backup-'.$q['commit'];
                require_ok(!file_exists($backup),'Backup directory already exists');
                $next=$account.'/.sezam11-public-next';require_ok(!file_exists($next) && !is_link($next),'Pending public link exists');
                require_ok(symlink($current,$next),'Cannot prepare public link');
                require_ok(rename($doc,$backup),'Cannot preserve old WordPress directory');
                if(!rename($next,$doc)) { rename($backup,$doc);throw new RuntimeException('Activation failed; original directory restored'); }
                file_put_contents($root.'/legacy-root.json',json_encode(['path'=>$backup,'commit'=>$q['commit']]));
            }
            $answer=['standalone'=>true,'wordpress_preserved_outside_public_root'=>true];
        } elseif($action==='restore-legacy') {
            require_ok($standalone && $target==='production','Standalone production not active');
            $legacy=json_decode(file_get_contents($root.'/legacy-root.json'),true,512,JSON_THROW_ON_ERROR);
            require_ok(dirname($legacy['path'])===$account && strpos(basename($legacy['path']),'.sezam11-wordpress-backup-')===0 && is_file($legacy['path'].'/wp-config.php'),'Legacy root invalid');
            // Only our public symlink is removed. The old WordPress directory is restored intact.
            require_ok(unlink($doc),'Cannot remove managed public symlink');require_ok(rename($legacy['path'],$doc),'Cannot restore preserved directory');
            $answer=['legacy_restored'=>true];
        } else { throw new RuntimeException('Unknown action'); }
        flock($lock,LOCK_UN);fclose($lock);
    }
    echo json_encode($answer,JSON_THROW_ON_ERROR)."\n";
} catch(Throwable $e) { fwrite(STDERR,$e->getMessage()."\n");exit(1); }
