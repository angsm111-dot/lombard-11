"""Build static service pages, blog listing and individual articles from structured data."""
from pathlib import Path
import json,html,re
root=Path(__file__).resolve().parents[1];dist=root/'dist'
esc=html.escape
wa=(root/'scripts/whatsapp.svg').read_text()
arrow='<svg class="arrow-inline" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 13 13 3M3 3h10v10"/></svg>'
def whatsapp(text='Napisz na WhatsApp'):
 return '<a class="button whatsapp" href="https://wa.me/48601775146" target="_blank" rel="noopener noreferrer">'+wa+'<span>'+text+'</span></a>'
posts=json.loads((dist/'data/articles.json').read_text())
def cards():
 return ''.join('<a class="article-card" href="/blog/'+esc(p['slug'])+'/"><div class="article-photo"><img src="'+esc(p['image'])+'" alt="'+esc(p['imageAlt'])+'" width="640" height="426" loading="lazy"></div><div class="article-meta"><span>'+esc(p['category'])+'</span><span>'+str(p['readTime'])+' min czytania</span></div><h3>'+esc(p['title'])+'</h3><p>'+esc(p['excerpt'])+'</p><span class="article-more">Przeczytaj poradnik '+arrow+'</span></a>' for p in posts)
p=dist/'index.html';source=p.read_text()
if '<!-- BLOG_CARDS_START -->' not in source:source=source.replace('<div id="articles" class="articles"></div>','<!-- BLOG_CARDS_START --><div id="articles" class="articles"></div><!-- BLOG_CARDS_END -->')
source=re.sub(r'<!-- BLOG_CARDS_START -->.*?<!-- BLOG_CARDS_END -->','<!-- BLOG_CARDS_START --><div id="articles" class="articles">'+cards()+'</div><!-- BLOG_CARDS_END -->',source,flags=re.S)
source=source.replace('↗',arrow);p.write_text(source)
header=source[source.index('<body>')+6:source.index('<main id="main">')].replace('href="#main"','href="#main"')
footer=source[source.index('<footer'):source.index('</body>')]
def page(title,description,body,kind='article-page',path=None):
 nav=header
 if path:nav=nav.replace('href="'+path+'"','aria-current="page" href="'+path+'"')
 return '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#783e38"><title>'+esc(title)+' | Lombard 11 — Sezam</title><meta name="description" content="'+esc(description,quote=True)+'"><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css"><script defer src="/app.js"></script></head><body>'+nav+'<main id="main" class="wrap '+kind+'">'+body.replace('↗',arrow)+'</main>'+footer+'</body></html>'
def write(slug,title,description,body,kind='article-page'):
 path=dist/slug;path.mkdir(parents=True,exist_ok=True);(path/'index.html').write_text(page(title,description,body,kind,'/'+slug+'/'))
def intro(title,description,label='LOMBARD 11 / SEZAM'):
 return '<a class="back-link" href="/">← Strona główna</a><div class="eyebrow">'+label+'</div><h1>'+title+'</h1><p class="page-lead">'+description+'</p>'
def cta():
 return '<aside class="page-cta"><h2>Porozmawiajmy o Twoim przedmiocie.</h2><p>Napisz, zadzwoń lub odwiedź nas przy ul. Pocztowej 11 w Gorzowie Wielkopolskim. Ostateczną wycenę potwierdzamy po obejrzeniu przedmiotu.</p><div class="actions">'+whatsapp()+'<a class="text-link" href="/kontakt/">Dane kontaktowe i dojazd ↗</a></div></aside>'
for post in posts:
 body='<a class="back-link" href="/blog/">← Wszystkie poradniki</a><div class="article-meta">'+esc(post['category'])+' · '+str(post['readTime'])+' min czytania</div><h1>'+esc(post['title'])+'</h1><p class="page-lead">'+esc(post['excerpt'])+'</p><figure class="article-cover"><img src="'+esc(post['image'])+'" alt="'+esc(post['imageAlt'])+'" width="1200" height="800"><figcaption>Zdjęcie ilustracyjne</figcaption></figure>'
 body+=''.join('<section><h2>'+esc(s['heading'])+'</h2><p>'+esc(s['text'])+'</p></section>' for s in post['sections'])
 write('blog/'+post['slug'],post['title'],post['excerpt'],body+cta())
write('blog','Poradnik i blog','Praktyczne poradniki o złocie, metalach szlachetnych i sprzedaży elektroniki.',intro('Wiedza, która <em>pomaga wybrać.</em>','O metalach szlachetnych, wycenie i przygotowaniu przedmiotów do sprzedaży. Każdy poradnik znajdziesz pod osobnym adresem.','PORADNIK / BLOG')+'<div class="articles blog-list">'+cards()+'</div>','content-page')
metals=[('zlota','Złoto','Au','Skup złota','Biżuteria, złom złota i wyroby ze złota. Sprawdź, jak przygotować się do wyceny.',['Biżuteria: pierścionki, obrączki, łańcuszki i kolczyki.','Uszkodzone wyroby i pojedyncze elementy biżuterii.','Monety oraz sztabki — po indywidualnej weryfikacji.'],[('333','33,3%'),('585','58,5%'),('750','75,0%'),('999','99,9%')]),('srebra','Srebro','Ag','Skup srebra','Srebrna biżuteria, monety i inne wyroby. Przy wycenie liczą się skład oraz masa kruszcu.',['Biżuteria srebrna, również uszkodzona.','Srebrne monety i sztabki — po weryfikacji.','Inne wyroby srebrne po sprawdzeniu składu; przedmioty posrebrzane wymagają osobnej oceny.'],[('800','80,0%'),('835','83,5%'),('925','92,5%'),('999','99,9%')]),('platyny','Platyna','Pt','Skup platyny','Masz przedmiot, który może zawierać platynę? Zacznij od sprawdzenia składu.',['Biżuteria i inne wyroby zawierające platynę — po potwierdzeniu składu.','Przedmioty z oznaczeniem próby, dokumentacją lub certyfikatem, jeśli je posiadasz.','Możliwość przyjęcia konkretnego przedmiotu potwierdzamy indywidualnie.'],[]),('palladu','Pallad','Pd','Skup palladu','Wycena palladu wymaga rozpoznania materiału i zawartości metalu. Skontaktuj się z nami przed wizytą.',['Wyroby i materiały zawierające pallad — po indywidualnej ocenie.','Dostępne oznaczenia i dokumentacja pomagają ustalić zakres weryfikacji.','Nie każdy materiał nadaje się do przyjęcia. Opisz przedmiot i zapytaj o możliwość wyceny.'],[])]
for slug,name,symbol,title,description,items,rates in metals:
 body=intro(title,description,'SKUP METALI SZLACHETNYCH')+'<div class="service-layout"><section><h2>Co możesz przynieść?</h2><ul class="content-list">'+''.join('<li>'+x+'</li>' for x in items)+'</ul><h2>Jak ustalamy wartość?</h2><p>Sprawdzamy rodzaj materiału, zawartość metalu oraz masę uwzględnianą w rozliczeniu. Cenę i warunki przedstawiamy przed zawarciem transakcji.</p><p>Jeśli skład budzi wątpliwości, zapytaj o <a href="/badanie-spektrometrem/">badanie spektrometrem</a>. Wynik pomiaru wymaga interpretacji, zwłaszcza w przypadku powłok i niejednorodnych wyrobów.</p></section><aside class="metal-summary"><span>'+symbol+'</span><h2>'+name+'</h2><p>Sprawdzenie materiału.<br>Indywidualna wycena.<br>Jasne ustalenia przed sprzedażą.</p><a class="button primary" href="tel:+48601775146">Zapytaj o cenę ↗</a></aside></div>'
 if rates:body+='<section class="service-prices"><h2>Cennik skupu '+slug+'</h2><p>Aktualne stawki potwierdzisz telefonicznie. Nie publikujemy niepotwierdzonych cen.</p><div class="price-card"><table><thead><tr><th scope="col">Próba</th><th scope="col">Zawartość metalu</th><th scope="col">Cena za gram</th></tr></thead><tbody>'+''.join('<tr><th scope="row">'+a+'</th><td>'+b+'</td><td>Zapytaj o cenę</td></tr>' for a,b in rates)+'</tbody></table></div></section>'
 else:body+='<section><h2>Cena ustalana indywidualnie</h2><p>Stawka zależy od potwierdzonej zawartości metalu i rodzaju materiału. Prześlij zdjęcie oraz opis przedmiotu, aby ustalić następny krok.</p></section>'
 write('skup-'+slug,title,description,body+cta(),'content-page')
category_data=[('zloto-i-bizuteria','Złoto i biżuteria','Pierścionki, obrączki, łańcuszki, kolczyki, monety i inne wyroby z metali szlachetnych.','Zabierz przedmiot i dostępne informacje o próbie lub pochodzeniu. Nie usuwaj kamieni ani nie stosuj agresywnych środków czyszczących przed wizytą.','/skup-zlota/','Dowiedz się więcej o skupie złota'),('telefony','Telefony','Smartfony i dostępne akcesoria. Wycena zależy między innymi od modelu, sprawności i stanu urządzenia.','Naładuj telefon i zabierz ładowarkę oraz dostępne akcesoria. Przed przekazaniem urządzenia wykonaj kopię danych, usuń blokady kont i kartę SIM.','/blog/przygotowanie-telefonu/','Przeczytaj poradnik przed sprzedażą'),('laptopy-i-elektronika','Laptopy i elektronika','Laptopy, konsole i inne urządzenia elektroniczne — po sprawdzeniu modelu, stanu oraz działania.','Zabierz zasilacz i akcesoria. Zabezpiecz swoje dane, wyloguj prywatne konta i przygotuj urządzenie do sprawdzenia.','/kontakt/','Zapytaj o swoje urządzenie'),('sprzet-i-rowery','Sprzęt i rowery','Elektronarzędzia, sprzęt techniczny oraz rowery. Możliwość przyjęcia potwierdzamy po ocenie przedmiotu.','Przygotuj model, opis stanu i dostępne wyposażenie. Przed wizytą możesz przesłać zdjęcia przez WhatsApp.','/kontakt/','Zapytaj o swój przedmiot')]
category_cards=''
for slug,title,desc,preparation,url,label in category_data:
 category_cards+='<a class="service-tile" href="/co-przyjmujemy/'+slug+'/"><h2>'+title+' ↗</h2><p>'+desc+'</p></a>'
 write('co-przyjmujemy/'+slug,title,desc,intro(title,desc,'CO PRZYJMUJEMY')+'<section><h2>Jak przygotować się do wizyty?</h2><p>'+preparation+'</p><h2>Co wpływa na wycenę?</h2><p>Oceniamy stan, kompletność i możliwość dalszej sprzedaży przedmiotu. W przypadku metali szlachetnych sprawdzamy także skład i masę kruszcu.</p><a class="text-link" href="'+url+'">'+label+' ↗</a></section>'+cta())
write('co-przyjmujemy','Co przyjmujemy','Sprawdź kategorie przedmiotów przyjmowanych w Lombardzie Sezam.',intro('Co możesz do nas <em>przynieść?</em>','Wybierz kategorię, żeby sprawdzić szczegóły i przygotować się do wizyty.')+'<div class="service-tiles">'+category_cards+'</div><p>Możliwość przyjęcia i ofertę potwierdzamy po indywidualnej ocenie przedmiotu.</p>'+cta(),'content-page')
# Reuse complete homepage sections for consistent services and contact details.
spectro=re.search(r'<section id="spektrometr".*?</section>',source,re.S).group()
spectro=spectro.replace('class="section wrap spectro"','class="section spectro"')
write('badanie-spektrometrem','Badanie spektrometrem','Sprawdzenie składu metali szlachetnych w Gorzowie Wielkopolskim.',intro('Badanie <em>spektrometrem.</em>','Sprawdzamy skład metalu i omawiamy, co oznacza wynik badania.')+spectro+cta(),'content-page')
offer=re.search(r'<section id="oferta".*?</section>',source,re.S).group().replace('class="wrap olx-inner"','class="olx-inner"')
write('oferta','Aktualna oferta OLX','Aktualne ogłoszenia Lombardu Sezam: biżuteria, elektronika i inne przedmioty.',intro('Nasza aktualna <em>oferta.</em>','Zdjęcia konkretnych przedmiotów, ceny i dostępność sprawdzisz bezpośrednio na naszym profilu OLX.')+offer,'content-page')
contact=re.search(r'<section id="kontakt".*?</section>',source,re.S).group().replace('class="wrap contact-grid"','class="contact-grid"')
write('kontakt','Kontakt i dojazd','Lombard Sezam, Pocztowa 11, Gorzów Wielkopolski. Telefon i WhatsApp: 601 775 146.',intro('Jesteśmy <em>po sąsiedzku.</em>','Odwiedź nas na Pocztowej 11, zadzwoń lub napisz na WhatsApp.')+contact,'content-page contact-page')
# Preserve the existing privacy information, updating the shared shell.
privacy=dist/'prywatnosc/index.html'
old=privacy.read_text();body=re.search(r'<main id="main"[^>]*>(.*?)</main>',old,re.S).group(1)
privacy.write_text(page('Prywatność','Informacje o prywatności na stronie Lombard 11.',body,path='/prywatnosc/'))
(dist/'404.html').write_text(page('Nie znaleziono strony','Wróć do strony głównej Lombard 11.',intro('Tu jeszcze nic nie ma.','Ten adres nie prowadzi do dostępnej strony.')+'<a class="button primary" href="/">Wróć na stronę główną →</a>'))
print('Generated',len(list(dist.rglob('*.html'))),'standalone HTML pages.')
