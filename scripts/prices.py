"""Render a timestamped panel snapshot; browser code refreshes it from the same public API."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,html
snapshot=json.loads((Path(__file__).resolve().parents[1]/'dist/data/prices.json').read_text())
def price_cell(metal,purity):
 value=snapshot.get('metals',{}).get(metal,{}).get(str(purity))
 label=f'{value:.2f}'.replace('.',',')+' zł/g' if isinstance(value,(int,float)) else 'Potwierdź cenę'
 return '<td data-price-cell="'+metal+'" data-purity="'+str(purity)+'">'+label+'</td>'
def price_status(metal,css='price-notice'):
 stamp=datetime.fromisoformat(snapshot['fetchedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Warsaw')).strftime('%d.%m.%Y, %H:%M')
 return '<p class="'+css+'" data-price-status="'+metal+'" aria-live="polite">Cennik Sezam · odczyt: '+stamp+'</p>'
def table(metal,rates):
 return '<table><thead><tr><th scope="col">Próba</th><th scope="col">Zawartość metalu</th><th scope="col">Cena skupu za gram</th></tr></thead><tbody>'+''.join('<tr'+(' class="featured"' if str(a)=='585' else '')+'><th scope="row">'+html.escape(str(a))+'</th><td>'+html.escape(str(b))+'</td>'+price_cell(metal,a)+'</tr>' for a,b in rates)+'</tbody></table>'
