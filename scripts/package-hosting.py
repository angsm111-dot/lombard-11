"""Package static website for a separate external hosting document root."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
archive=root.parent/'lombard11-hosting.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for path in sorted((root/'dist').rglob('*')):
  if path.is_file():z.write(path,path.relative_to(root/'dist'))
 z.write(root/'hosting/apache.htaccess','.htaccess')
 # Keep migration notes outside the public website package.
print(archive)
