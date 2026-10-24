# Lombard11.pl — przygotowanie podmiany strony

## Stan sprawdzony 24 października 2026

- `https://www.lombard11.pl/` przekierowuje na `https://lombard11.pl/`.
- Obecna strona działa na WordPressie i pokazuje komunikat „Strona w budowie”, z odesłaniem do sezam.com.pl.
- Publiczne serwery DNS: `adaline.ns.cloudflare.com` i `lamar.ns.cloudflare.com`.
- Publiczne adresy A są adresami proxy Cloudflare, a nie potwierdzonymi adresami hostingu źródłowego.
- Nie ustalono nazwy hostingodawcy ani dostępu do jego panelu/FTP/SFTP. Odpowiedź „rOBIMIMY.L11” nie identyfikuje usługodawcy.
- Niczego nie zmieniono w DNS, na starym hostingu, w bazie WordPressa ani w poczcie.

## Co zawiera nowa wersja

Statyczne pliki z katalogu `dist/`, bez potrzeby uruchamiania WordPressa. Blog ma 11 odrębnych artykułów, w tym 8 nowych. Każdy wpis i dział mają osobny plik HTML. Sitemap i adresy canonical wskazują `https://lombard11.pl`, zgodnie z obecnym przekierowaniem www. Obie wersje domeny mają prowadzić do tej samej strony.

## Czynności po uzyskaniu dostępu

1. Sprawdzić, jaki katalog obsługuje domenę i czy WordPress dzieli hosting z innymi stronami. Potwierdzić Apache/LiteSpeed albo Nginx i możliwość używania statycznych plików HTML.
2. Wykonać pełną kopię plików starej strony oraz eksport bazy danych. Zachować kopię poza publicznym katalogiem witryny. Zapisać dotychczasowy katalog domeny oraz reguły przekierowań.
3. Rozpakować zawartość paczki w **nowym, oddzielnym katalogu**. `index.html`, `assets/`, `blog/` itd. muszą leżeć bezpośrednio w katalogu witryny. Nie rozpakowywać nowej wersji na istniejącego WordPressa.
4. Sprawdzić stronę na chronionym adresie testowym. Adres testowy i dostęp do niego zależą od panelu hostingodawcy. Nie indeksować kopii testowej.
5. Uzupełnić pełne informacje o prywatności dla rzeczywistych usług i zweryfikować warunki reklamy pożyczki przed publicznym uruchomieniem. Nie zakładać, że tekst roboczy wyczerpuje wszystkie wymagania dla oferty finansowej.
6. Przełączyć katalog obsługiwany przez domenę na nową wersję. Jeżeli hosting zostaje ten sam, nie ma potrzeby automatycznej zmiany DNS. Zachować rekordy pocztowe MX/TXT i inne usługi.
7. Dla Apache/LiteSpeed paczka zawiera `.htaccess` z rozpoznanymi starymi adresami. Dla Nginx administrator musi zastosować równoważne reguły — `.htaccess` nie działa w Nginx. Sprawdzić dodatkowe stare adresy na podstawie eksportu WP/Search Console i uzupełnić mapę.
8. Potwierdzić HTTPS, przekierowanie www, strony artykułów, WhatsApp, OLX, sitemap oraz rzeczywisty kod 404 dla nieznanych adresów. Następnie wyczyścić cache Cloudflare i hostingu.
9. Zgłosić `/sitemap.xml` w Google Search Console. Samo wdrożenie metadanych nie gwarantuje pozycji ani natychmiastowej indeksacji.

## Wycofanie podmiany

Przywrócić poprzedni katalog domeny i jego reguły. Starej instalacji ani bazy nie usuwać przy podmianie. DNS nie zmieniać, jeśli nie był zmieniany podczas wdrożenia.

## Potrzebne do dokończenia

Dokładna nazwa i adres panelu hostingowego oraz autoryzowany dostęp do plików witryny. Jeśli DNS wymaga zmiany, także autoryzowany dostęp do odpowiedniej strefy Cloudflare. Haseł nie wpisywać do repozytorium ani zwykłych wiadomości; użyć obsługiwanego mechanizmu połączenia/sekretów.

## Ważne ustalenie: wcześniejszy blog nadal istnieje

Publiczne API WordPress pozwoliło odnaleźć dawniej opublikowane wpisy i strony, mimo komunikatu serwisowego na stronie głównej. Ich adresy i tytuły są w `hosting/legacy-url-inventory.csv`. Eksport publicznych tekstów zapisano osobno jako `lombard11-publiczny-eksport-wp.zip`; nie zastępuje on pełnego backupu bazy i mediów.

Przed przełączeniem domeny należy zachować lub przenieść starsze artykuły, a tam, gdzie istnieje zgodny tematycznie następca, ustawić przekierowanie 301. Obecna paczka nowej strony zawiera nowy blog i przekierowania rozpoznanych stron usługowych, ale NIE przenosi automatycznie całego archiwum starego WordPressa. Nie wolno traktować podmiany katalogu jako zatwierdzenia usunięcia dawnego bloga. Treści historyczne, zwłaszcza ceny i porady finansowe, wymagają przeglądu aktualności zamiast automatycznego przedrukowania jako nowych artykułów.
