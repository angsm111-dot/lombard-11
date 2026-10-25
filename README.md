# Lombard 11 — Sezam

Pierwszy projekt strony informacyjnej lombardu. Responsywna strona statyczna w HTML, CSS i JavaScript, bez zależności wykonawczych.

## Podgląd lokalny

```sh
python3 -m http.server 8000 --directory dist
```

## Zawartość

- Skup złota z cennikiem podłączonym do publicznego API panelu Sezam. Stawki są odświeżane co 5 minut; nie przeliczamy ponownie potrąceń.
- Informacja o badaniu spektrometrem.
- Kategorie przyjmowanych przedmiotów.
- Bezpośredni link do oferty OLX Sezam.
- Kontakt i pływający przycisk WhatsApp.
- Trzy poradniki z osobnymi adresami, zapisane jako uporządkowane dane.

## Przyszły system publikacji

Źródło artykułów: `dist/data/articles.json`. Każdy wpis ma stabilne `id`, `slug`, kategorię, zajawkę i sekcje tekstowe. Integracja z centralnym systemem CMS nie jest jeszcze wykonana. Po zmianie danych uruchom `python3 scripts/build.py`, aby wygenerować strony wpisów. Lista na stronie bloga jest generowana z tego samego pliku. Treści są escapowane przy generowaniu i renderowane przez textContent w przeglądarce.

## Dane i zasoby

Dane kontaktowe potwierdzone przez właściciela: Pocztowa 11, Gorzów Wielkopolski; telefon i WhatsApp 601 775 146. Logo pobrane z sezam.com.pl na prośbę właściciela. OLX: https://www.olx.pl/oferty/uzytkownik/G2XGE/. Zdjęcie biżuterii wygenerowane na potrzeby projektu; nie przedstawia rzeczywistego stanu magazynowego.

## Do uzupełnienia

Ewentualny koszt badania, pełna informacja o prywatności i umowa API z przyszłym CMS. Publikacja Sites jest prywatna do czasu zmiany dostępu przez właściciela.

## Osobne strony HTML

Każda pozycja menu ma oddzielny adres i plik `index.html`: `/skup-zlota/`, `/skup-srebra/`, `/skup-platyny/`, `/skup-palladu/`, `/co-przyjmujemy/`, `/oferta/`, `/blog/` i `/kontakt/`. Kategorie przedmiotów mają strony w `/co-przyjmujemy/<kategoria>/`, a pojedyncze teksty w `/blog/<slug>/`. Dostępna jest też strona `/badanie-spektrometrem/`.

`python3 scripts/build.py` generuje te strony oraz statyczne karty poradników ze wspólnego pliku `dist/data/articles.json`. Lista artykułów działa bez JavaScript. Wspólne menu i stopka pochodzą z plików `templates/header.html` i `templates/footer.html`. Nie ma jeszcze połączenia z centralnym CMS.

Fotografie poradników są wygenerowanymi zdjęciami ilustracyjnymi; nie pokazują rzeczywistych urządzeń firmy ani aktualnych przedmiotów w sprzedaży. Ilustracje spektrometru i telefonu znajdują się w `dist/assets/blog-*.webp`.

## Blog i SEO dla lombard11.pl

Blog zawiera 11 artykułów (8 nowych poradników lokalnych) i wyraźny odnośnik z ikoną w menu. Każdy wpis ma oddzielną stronę HTML. Generator tworzy canonical, Open Graph, LocalBusiness, BlogPosting, `robots.txt` i `sitemap.xml` dla domeny `https://lombard11.pl`, zgodnie z obecnym przekierowaniem www.

`python3 scripts/package-hosting.py` tworzy paczkę do niezależnego katalogu hostingu. Instrukcja i wynik audytu domeny: `hosting/MIGRACJA.md`. Znaleziono także stary blog WordPress; przed przełączeniem domeny należy zachować jego treści i rozliczyć adresy z `hosting/legacy-url-inventory.csv`. Przygotowanie paczki nie oznacza podłączenia domeny ani wdrożenia na istniejącym hostingu.

## Kafelki przyjmowanych przedmiotów

Źródło kategorii: `dist/data/categories.json`. Generator tworzy z niego siedem kafelków ze zdjęciami na stronie `/co-przyjmujemy/` oraz osobne podstrony kategorii. Fotografie z prefiksem `kategoria-` są ilustracyjne, wygenerowane do projektu. Wygaszenie obrazu i dopasowanie do tła realizuje CSS. Dawny adres `/co-przyjmujemy/sprzet-i-rowery/` pozostaje dostępny.

## Integracja cen z panelem Sezam

Źródło: `https://skup-zlota-gorzow.angsm111.workers.dev/api/prices`, projekt `angsm111-dot/nowa-skup-zlota-gorzow`. Pobierane są gotowe wartości `metals.gold.purities[próba].price` oraz analogiczne ceny srebra. Nigdy nie pobieramy hasła administratora i nie zmieniamy ustawień panelu.

`dist/prices.js` odświeża publiczny cennik co pięć minut oraz po powrocie do karty. Korzysta z CORS, bez poświadczeń. Sprawdza kompletność, poprawność cen i czas źródła; odrzuca dane zapasowe oraz odczyty starsze niż 30 minut. Przy awarii zachowuje wyłącznie świeży, potwierdzony odczyt, a po jego wygaśnięciu pokazuje kontakt zamiast nieaktualnych stawek.

`dist/data/prices.json` jest oznaczonym czasem odczytu snapshotem do renderowania HTML, nie osobnym edytowalnym cennikiem. Skrypt synchronizacji wymaga narzędzia `curl`. Aby odświeżyć go przed budową, uruchom `python3 scripts/sync-prices.py`, a potem `python3 scripts/build.py`. Bez JavaScript widoczny jest zapisany odczyt z jego datą, nie automatyczne aktualizacje. Skrypt nie korzysta z panelu administracyjnego do zapisu.

## Podział na osobne działy

Strona główna jest krótkim wprowadzeniem z odnośnikami do działów; nie zawiera pełnego kontaktu, cennika, listy kategorii ani artykułów. Treść główna: `templates/home.html`. Dedykowane sekcje kontaktu, oferty i spektrometru są w odpowiednich plikach `templates/`, a generator publikuje je tylko na właściwych podstronach.

Menu: Co przyjmujemy → Skup metali szlachetnych → Na sprzedaż → Badanie spektrometrem → Blog / poradnik → Kontakt. Badanie spektrometrem jest osobną pozycją głównego menu. Ogólny przegląd metali ma adres `/skup-metali-szlachetnych/`. Cennik i skrypt cen ładowane są na stronach złota i srebra. Dawne linki do sekcji strony głównej przekierowują do odpowiednich podstron.
