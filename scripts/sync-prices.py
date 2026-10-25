"""Read the public Sezam panel feed; never access admin credentials or recompute margins."""
import json,subprocess
from pathlib import Path
URL='https://skup-zlota-gorzow.angsm111.workers.dev/api/prices'
def extract(data):
 if data.get('status')!='ok' or data.get('provider')=='Dane zapasowe':raise ValueError('Price feed is not confirmed')
 result={'source':URL,'provider':data['provider'],'fetchedAt':data['fetchedAt'],'configUpdatedAt':data.get('configUpdatedAt'),'metals':{}}
 for metal in ('gold','silver'):
  result['metals'][metal]={str(k):v['price'] for k,v in data['metals'][metal]['purities'].items() if isinstance(v.get('price'),(int,float)) and v['price']>0}
 return result
if __name__=='__main__':
 data=json.loads(subprocess.check_output(['curl','--silent','--show-error','--fail','--max-time','20',URL],text=True))
 p=Path(__file__).resolve().parents[1]/'dist/data/prices.json'
 p.write_text(json.dumps(extract(data),ensure_ascii=False,indent=2)+'\n')
 print('Updated confirmed panel price snapshot:',data['fetchedAt'])
