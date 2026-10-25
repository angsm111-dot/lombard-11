"""Build static service pages, blog listing and individual articles from structured data."""
from pathlib import Path
import json,html,re
from prices import snapshot,price_cell,price_status,table as price_table
root=Path(__file__).resolve().parents[1];dist=root/'dist'
esc=html.escape
wa=(root/'scripts/whatsapp.svg').read_text()
arrow='<svg class="arrow-inline" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 13 13 3M3 3h10v10"/></svg>'
def whatsapp(text='Napisz na WhatsApp'):
 return '<a class="button whatsapp" href="https://wa.me/48601775146" target="_blank" rel="noopener noreferrer">'+wa+'<span>'+text+'</span></a>'
posts=json.loads((dist/'data/articles.json').read_text())
def cards(limit=None):
 return ''.join('<a class="article-card" href="/blog/'+esc(p['slug'])+'/"><div class="article-photo"><img src="'+esc(p['image'])+'" alt="'+esc(p['imageAlt'])+'" width="640" height="426" loading="lazy"></div><div class="article-meta"><span>'+esc(p['category'])+'</span><span>'+str(p['readTime'])+' min czytania</span></div><h3>'+esc(p['title'])+'</h3><p>'+esc(p['excerpt'])+'</p><span class="article-more">Przeczytaj poradnik '+arrow+'</span></a>' for p in (posts if limit is None else posts[:limit]))
categories=json.loads((dist/'data/categories.json').read_text())
def category_card(category,index,listing=False):
 heading='h2' if listing else 'h3'
 css='service-tile photo-tile' if listing else 'category photo-tile'
 return '<a class="'+css+'" href="/co-przyjmujemy/'+esc(category['slug'])+'/"><img class="category-photo" src="'+esc(category['image'],quote=True)+'" alt="" width="640" height="426" loading="lazy"><span class="category-number">'+str(index+1).zfill(2)+'</span><div class="category-copy"><'+heading+'>'+esc(category['title'])+'</'+heading+'><p>'+esc(category['summary'])+'</p><span class="category-more">Sprawdź szczegóły '+arrow+'</span></div></a>'
templates=root/'templates'
header=(templates/'header.html').read_text().strip()
footer=(templates/'footer.html').read_text().strip()
p=dist/'index.html';source=p.read_text()
head=source[:source.index('<body>')+6]
head=head.replace('<script src="/prices.js" defer></script>','')
home=(templates/'home.html').read_text().replace('↗',arrow)
source=head+header+'<main id="main">'+home+'</main>'+footer+'</body></html>'
p.write_text(source)
def page(title,description,body,kind='article-page',path=None):
 nav=header
 if path:nav=nav.replace('href="'+path+'"','aria-current="page" href="'+path+'"')
 price_script='<script defer src="/prices.js"></script>' if 'data-price-cell' in body else ''
 return '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#783e38"><title>'+esc(title)+' | Lombard 11 — Sezam</title><meta name="description" content="'+esc(description,quote=True)+'"><link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css"><script defer src="/app.js"></script>'+price_script+'</head><body>'+nav+'<main id="main" class="wrap '+kind+'">'+body.replace('↗',arrow)+'</main>'+footer+'</body></html>'
def write(slug,title,description,body,kind='article-page'):
 path=dist/slug;path.mkdir(parents=True,exist_ok=True);(path/'index.html').write_text(page(title,description,body,kind,'/'+slug+'/'))
def intro(title,description,label='LOMBARD 11 / SEZAM'):
 return '<a class="back-link" href="/">← Strona główna</a><div class="eyebrow">'+label+'</div><h1>'+title+'</h1><p class="page-lead">'+description+'</p>'
def cta():
 return '<aside class="page-cta"><h2>Porozmawiajmy o Twoim przedmiocie.</h2><p>Napisz, zadzwoń lub odwiedź nas przy ul. Pocztowej 11 w Gorzowie Wielkopolskim. Ostateczną wycenę potwierdzamy po obejrzeniu przedmiotu.</p><div class="actions">'+whatsapp()+'<a class="text-link" href="/kontakt/">Dane kontaktowe i dojazd ↗</a></div></aside>'
for post in posts:
 body='<a class="back-link" href="/blog/">← Wszystkie poradniki</a><div class="article-meta">'+esc(post['category'])+' · '+str(post['readTime'])+' min czytania</div><h1>'+esc(post['title'])+'</h1><p class="page-lead">'+esc(post['excerpt'])+'</p><figure class="article-cover"><img src="'+esc(post['image'])+'" alt="'+esc(post['imageAlt'])+'" width="1200" height="800"><figcaption>Zdjęcie ilustracyjne</figcaption></figure>'
 body+=''.join('<section><h2>'+esc(s['heading'])+'</h2><p>'+esc(s['text'])+'</p></section>' for s in post['sections'])
 if post.get('relatedLinks'):
  body+='<aside class="related-reading"><h2>Sprawdź również</h2><ul>'+''.join('<li><a href="'+esc(link['href'],quote=True)+'">'+esc(link['label'])+'</a></li>' for link in post['relatedLinks'])+'</ul></aside>'
 write('blog/'+post['slug'],post['title'],post['excerpt'],body+cta())
write('blog','Poradnik i blog','Praktyczne poradniki o złocie, metalach szlachetnych i sprzedaży elektroniki.',intro('Blog Sezam.<br><em>Praktycznie o lombardzie w Gorzowie.</em>','Jak kupować w lombardzie, przygotować złoty złom do wyceny i wybierać używaną elektronikę? Przeczytaj poradniki zespołu Sezam przy Pocztowej 11.','BLOG / PORADNIK')+'<div class="articles blog-list">'+cards()+'</div>','content-page')
metals=[('zlota','Złoto','Au','Skup złota','Biżuteria, złom złota i wyroby ze złota. Sprawdź, jak przygotować się do wyceny.',['Biżuteria: pierścionki, obrączki, łańcuszki i kolczyki.','Uszkodzone wyroby i pojedyncze elementy biżuterii.','Monety oraz sztabki — po indywidualnej weryfikacji.'],[('333','33,3%'),('585','58,5%'),('750','75,0%'),('999','99,9%')]),('srebra','Srebro','Ag','Skup srebra','Srebrna biżuteria, monety i inne wyroby. Przy wycenie liczą się skład oraz masa kruszcu.',['Biżuteria srebrna, również uszkodzona.','Srebrne monety i sztabki — po weryfikacji.','Inne wyroby srebrne po sprawdzeniu składu; przedmioty posrebrzane wymagają osobnej oceny.'],[('800','80,0%'),('835','83,5%'),('925','92,5%'),('999','99,9%')]),('platyny','Platyna','Pt','Skup platyny','Masz przedmiot, który może zawierać platynę? Zacznij od sprawdzenia składu.',['Biżuteria i inne wyroby zawierające platynę — po potwierdzeniu składu.','Przedmioty z oznaczeniem próby, dokumentacją lub certyfikatem, jeśli je posiadasz.','Możliwość przyjęcia konkretnego przedmiotu potwierdzamy indywidualnie.'],[]),('palladu','Pallad','Pd','Skup palladu','Wycena palladu wymaga rozpoznania materiału i zawartości metalu. Skontaktuj się z nami przed wizytą.',['Wyroby i materiały zawierające pallad — po indywidualnej ocenie.','Dostępne oznaczenia i dokumentacja pomagają ustalić zakres weryfikacji.','Nie każdy materiał nadaje się do przyjęcia. Opisz przedmiot i zapytaj o możliwość wyceny.'],[])]
for slug,name,symbol,title,description,items,rates in metals:
 body=intro(title,description,'SKUP METALI SZLACHETNYCH')+'<div class="service-layout"><section><h2>Co możesz przynieść?</h2><ul class="content-list">'+''.join('<li>'+x+'</li>' for x in items)+'</ul><h2>Jak ustalamy wartość?</h2><p>Sprawdzamy rodzaj materiału, zawartość metalu oraz masę uwzględnianą w rozliczeniu. Cenę i warunki przedstawiamy przed zawarciem transakcji.</p><p>Jeśli skład budzi wątpliwości, zapytaj o <a href="/badanie-spektrometrem/">badanie spektrometrem</a>. Wynik pomiaru wymaga interpretacji, zwłaszcza w przypadku powłok i niejednorodnych wyrobów.</p></section><aside class="metal-summary"><span>'+symbol+'</span><h2>'+name+'</h2><p>Sprawdzenie materiału.<br>Indywidualna wycena.<br>Jasne ustalenia przed sprzedażą.</p><a class="button primary" href="tel:+48601775146">Zapytaj o cenę ↗</a></aside></div>'
 if rates:
  metal='gold' if slug=='zlota' else 'silver'
  if metal=='gold':rates=[(purity,f'{int(purity)/10:.1f}%'.replace('.',',')) for purity in sorted(snapshot['metals']['gold'],key=int)]
  pricing='<section class="service-prices"><h2>Cennik skupu '+('złota' if metal=='gold' else 'srebra')+'</h2>'+price_status(metal,'live-price-status')+'<div class="price-card">'+price_table(metal,rates)+'</div><p class="price-explanation">Cena za 1 gram wyrobu danej próby. Ostateczna wycena po sprawdzeniu materiału i masy.</p></section>'
  if metal=='gold':
   body=intro('Skup złota','Aktualne ceny skupu złota. Biżuteria i złom złota.','METALE SZLACHETNE')+pricing+'<section class="gold-details"><h2>Co przyjmujemy?</h2><p>Biżuterię, także uszkodzoną, oraz monety i sztabki po weryfikacji. Przynieś przedmiot — sprawdzimy próbę, masę i przedstawimy ofertę.</p><a class="text-link" href="/badanie-spektrometrem/">Sprawdź badanie spektrometrem ↗</a></section>'
  else:body+=pricing
 else:body+='<section><h2>Cena ustalana indywidualnie</h2><p>Stawka zależy od potwierdzonej zawartości metalu i rodzaju materiału. Prześlij zdjęcie oraz opis przedmiotu, aby ustalić następny krok.</p></section>'
 write('skup-'+slug,title,description,body+cta(),'content-page compact-gold-page' if slug=='zlota' else 'content-page')

metal_tiles=''.join('<a class="service-tile" href="/skup-'+slug+'/"><h2>'+title+' ↗</h2><p>'+description+'</p></a>' for slug,name,symbol,title,description,items,rates in metals)
write('skup-metali-szlachetnych','Skup metali szlachetnych','Skup złota, srebra, platyny i palladu w Gorzowie. Wybierz metal i sprawdź szczegóły.',intro('Skup metali <em>szlachetnych.</em>','Wybierz metal, żeby zobaczyć cennik i informacje o wycenie.')+'<div class="service-tiles">'+metal_tiles+'</div><a class="button primary" href="/badanie-spektrometrem/">Sprawdź badanie spektrometrem ↗</a>','content-page')

category_cards=''.join(category_card(c,i,True) for i,c in enumerate(categories))
for c in categories:
 body=intro(c['title'],c['description'],'CO PRZYJMUJEMY')+'<section><h2>Jak przygotować się do wizyty?</h2><p>'+esc(c['preparation'])+'</p><h2>Co wpływa na wycenę?</h2><p>Oceniamy stan, kompletność i możliwość dalszej sprzedaży przedmiotu. W przypadku metali szlachetnych sprawdzamy także skład i masę kruszcu.</p><a class="text-link" href="'+esc(c['link'],quote=True)+'">'+esc(c['linkLabel'])+' ↗</a></section>'
 if c['slug']=='zloto-i-bizuteria':body+='<p><a href="/skup-srebra/">Sprawdź również skup srebra ↗</a></p>'
 write('co-przyjmujemy/'+c['slug'],c['title'],c['description'],body+cta())
write('co-przyjmujemy','Co przyjmujemy','Złoto i srebro, telefony, laptopy, elektronika użytkowa, konsole do gier, rowery i sprzęt techniczny.',intro('Co możesz do nas <em>przynieść?</em>','Wybierz kategorię, żeby sprawdzić szczegóły i przygotować się do wizyty.')+'<div class="service-tiles">'+category_cards+'</div><p>Możliwość przyjęcia i ofertę potwierdzamy po indywidualnej ocenie przedmiotu.</p>'+cta(),'content-page')
# Keep the previously published combined category address available.
write('co-przyjmujemy/sprzet-i-rowery','Sprzęt i rowery','Sprawdź osobne kategorie rowerów i sprzętu technicznego.',intro('Sprzęt i rowery','Wybierz odpowiednią kategorię, żeby sprawdzić szczegóły.')+'<div class="service-tiles">'+''.join(category_card(c,i,True) for i,c in enumerate(categories) if c['slug'] in ('rowery','sprzet-techniczny'))+'</div>'+cta(),'content-page')
# Reuse complete homepage sections for consistent services and contact details.
spectro=(templates/'spektrometr.html').read_text()
spectro=spectro.replace('class="section wrap spectro"','class="section spectro"')
write('badanie-spektrometrem','Badanie spektrometrem','Sprawdzenie składu metali szlachetnych w Gorzowie Wielkopolskim.',intro('Badanie <em>spektrometrem.</em>','Sprawdzamy skład metalu i omawiamy, co oznacza wynik badania.')+spectro+cta(),'content-page')
offer=(templates/'oferta.html').read_text().replace('class="wrap olx-inner"','class="olx-inner"')
write('oferta','Na sprzedaż — oferta OLX','Aktualne ogłoszenia Lombardu Sezam: biżuteria, elektronika i inne przedmioty.',intro('Nasza aktualna <em>oferta.</em>','Zdjęcia konkretnych przedmiotów, ceny i dostępność sprawdzisz bezpośrednio na naszym profilu OLX.')+offer,'content-page')
contact=(templates/'kontakt.html').read_text().replace('class="wrap contact-grid"','class="contact-grid"')
write('kontakt','Kontakt i dojazd','Lombard Sezam, Pocztowa 11, Gorzów Wielkopolski. Telefon i WhatsApp: 601 775 146.',intro('Jesteśmy <em>po sąsiedzku.</em>','Odwiedź nas na Pocztowej 11, zadzwoń lub napisz na WhatsApp.')+contact,'content-page contact-page')
# Preserve the existing privacy information, updating the shared shell.
privacy=dist/'prywatnosc/index.html'
old=privacy.read_text();body=re.search(r'<main id="main"[^>]*>(.*?)</main>',old,re.S).group(1)
privacy.write_text(page('Prywatność','Informacje o prywatności na stronie Lombard 11.',body,path='/prywatnosc/'))
(dist/'404.html').write_text(page('Nie znaleziono strony','Wróć do strony głównej Lombard 11.',intro('Tu jeszcze nic nie ma.','Ten adres nie prowadzi do dostępnej strony.')+'<a class="button primary" href="/">Wróć na stronę główną →</a>'))
print('Generated',len(list(dist.rglob('*.html'))),'standalone HTML pages.')

write('pozyczki-pod-zastaw','Pożyczki pod zastaw w Gorzowie','Zapytaj o pożyczkę pod zastaw w Lombardzie Sezam przy Pocztowej 11 w Gorzowie.',intro('Pożyczka pod zastaw.<br><em>Porozmawiajmy o warunkach.</em>','Dla nowych klientów: 5% za miesiąc. Warunki konkretnej umowy przedstawiamy przed jej podpisaniem.')+'<section><h2>Od czego zacząć?</h2><p>Opisz przedmiot lub przynieś go do punktu przy Pocztowej 11 w Gorzowie Wielkopolskim. Sprawdzimy, czy możemy go przyjąć, i przedstawimy ofertę po ocenie jego wartości.</p><h2>Co ustalić przed podpisaniem?</h2><p>Zapytaj o kwotę pożyczki, pełną kwotę do zapłaty, termin oraz zasady odbioru przedmiotu. Oferta 5% za miesiąc dotyczy nowych klientów; szczegóły potwierdzamy w punkcie.</p><h2>Jak przygotować przedmiot?</h2><p>Do elektroniki zabierz dostępne akcesoria i zasilacz. Zabezpiecz swoje dane oraz przygotuj dokument tożsamości potrzebny do zawarcia transakcji. W przypadku biżuterii nie usuwaj kamieni i nie stosuj agresywnych środków czyszczących.</p><a class="text-link" href="/co-przyjmujemy/">Sprawdź, co przyjmujemy ↗</a></section>'+cta(),'content-page')

# Production SEO metadata. The existing domain already redirects www to the apex.
origin='https://lombard11.pl'
business={'@context':'https://schema.org','@type':'LocalBusiness','@id':origin+'/#business','name':'Lombard Sezam — Lombard 11','url':origin+'/','telephone':'+48601775146','image':origin+'/assets/hero.webp','address':{'@type':'PostalAddress','streetAddress':'ul. Pocztowa 11','addressLocality':'Gorzów Wielkopolski','postalCode':'66-400','addressCountry':'PL'},'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],'opens':'10:00','closes':'18:00'},{'@type':'OpeningHoursSpecification','dayOfWeek':'Saturday','opens':'10:00','closes':'14:00'}]}
article_map={'/blog/'+p['slug']+'/':p for p in posts}
urls=[]
for file in sorted(dist.rglob('*.html')):
 rel=file.relative_to(dist)
 route='/' if str(rel)=='index.html' else '/'+str(rel.parent)+'/'
 if file.name=='404.html':continue
 canonical=origin+route;urls.append(canonical)
 text=file.read_text()
 title=re.search(r'<title>(.*?)</title>',text,re.S).group(1)
 description=re.search(r'<meta name="description" content="([^"]*)"',text).group(1)
 post=article_map.get(route)
 image=origin+(post['image'] if post else '/assets/hero.webp')
 metadata='<link rel="canonical" href="'+canonical+'"><meta property="og:locale" content="pl_PL"><meta property="og:site_name" content="Lombard 11 — Sezam"><meta property="og:type" content="'+('article' if post else 'website')+'"><meta property="og:title" content="'+esc(html.unescape(title),quote=True)+'"><meta property="og:description" content="'+description+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="'+image+'">'
 schemas=[business]
 if post:
  schemas.append({'@context':'https://schema.org','@type':'BlogPosting','headline':post['title'],'description':post['excerpt'],'mainEntityOfPage':canonical,'image':image,'author':{'@type':'Organization','name':'Lombard Sezam'},'publisher':{'@type':'Organization','name':'PUH SEZAM Sp. z o.o.','logo':{'@type':'ImageObject','url':origin+'/assets/logo.png'}}})
 metadata+=''.join('<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'</script>' for data in schemas)
 # Re-running the builder must not duplicate metadata on the retained homepage.
 text=re.sub(r'<!-- SEO_START -->.*?<!-- SEO_END -->','',text,flags=re.S)
 text=text.replace('</head>','<!-- SEO_START -->'+metadata+'<!-- SEO_END --></head>')
 file.write_text(text)
(dist/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+esc(url)+'</loc></url>\n' for url in urls)+'</urlset>\n')
(dist/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+origin+'/sitemap.xml\n')
print('SEO: canonical, Open Graph, LocalBusiness, BlogPosting and sitemap for',len(urls),'pages.')
