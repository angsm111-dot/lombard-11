"""Generate static article pages from CMS-ready structured content."""
from pathlib import Path
import json,html
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
source=(dist/'index.html').read_text()
header=source[source.index('<body>')+6:source.index('<main id="main">')]
# Anchor links on article pages return to the homepage.
header=header.replace('href="#','href="/#')
footer=source[source.index('<footer>'):source.index('</body>')].replace('href="#main"','href="/#main"')
def page(title,description,body):
 return '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+' | Lombard 11 — Sezam</title><meta name="description" content="'+html.escape(description,quote=True)+'"><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css"><script defer src="/app.js"></script></head><body>'+header+'<main id="main" class="wrap article-page">'+body+'</main>'+footer+'</body></html>'
for post in json.loads((dist/'data/articles.json').read_text()):
 body='<a class="text-link" href="/#blog">← Wróć do poradników</a><div class="article-meta">'+html.escape(post['category'])+' · '+str(post['readTime'])+' min czytania</div><h1>'+html.escape(post['title'])+'</h1><p>'+html.escape(post['excerpt'])+'</p>'
 body+=''.join('<section><h2>'+html.escape(s['heading'])+'</h2><p>'+html.escape(s['text'])+'</p></section>' for s in post['sections'])
 body+='<a class="button primary" href="https://wa.me/48601775146" target="_blank" rel="noopener noreferrer">Masz pytanie? Napisz na WhatsApp ↗</a>'
 path=dist/'blog'/post['slug'];path.mkdir(parents=True,exist_ok=True)
 (path/'index.html').write_text(page(post['title'],post['excerpt'],body))
privacy=dist/'prywatnosc';privacy.mkdir(exist_ok=True)
(privacy/'index.html').write_text(page('Prywatność','Informacje o prywatności na stronie Lombard 11.','<a href="/">← Strona główna</a><h1>Prywatność</h1><p>Ta wersja strony informuje o ofercie Lombardu Sezam. Nie zawiera formularza kontaktowego, kont użytkowników ani narzędzi analitycznych.</p><h2>Kontakt i serwisy zewnętrzne</h2><p>Kontakt z firmą jest dostępny pod numerem 601 775 146 lub w punkcie przy ul. Pocztowej 11 w Gorzowie Wielkopolskim. Podmiot wskazany na stronie to PUH SEZAM Sp. z o.o.</p><p>Przyciski WhatsApp, OLX i Map Google prowadzą do zewnętrznych serwisów. Po przejściu do nich obowiązują zasady prywatności ich operatorów. Wysyłając wiadomość, udostępniasz dane wpisane przez siebie w wybranym serwisie.</p><h2>Zasoby i działanie strony</h2><p>Strona pobiera kroje pisma z Google Fonts. To połączenie przekazuje dostawcy dane techniczne żądania, w tym adres IP. Dostawca hostingu może przetwarzać dane techniczne potrzebne do udostępnienia i zabezpieczenia strony.</p><p>Przed uruchomieniem docelowej wersji publicznej informacje o administratorze, podstawach przetwarzania, okresach przechowywania i prawach osób zostaną uzupełnione odpowiednio do faktycznie używanych usług.</p>'))
(dist/'404.html').write_text(page('Nie znaleziono strony','Wróć do strony głównej Lombard 11.','<h1>Tu jeszcze nic nie ma.</h1><p>Ten adres nie prowadzi do dostępnej strony.</p><a class="button primary" href="/">Wróć na stronę główną →</a>'))
print('Generated 3 articles, privacy and 404 pages.')

# Inline vectors keep direction icons consistent across installed font sets.
arrow='<svg class="arrow-inline" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 13 13 3M3 3h10v10"/></svg>'
for file in dist.rglob('*.html'):
 file.write_text(file.read_text().replace('↗',arrow))
