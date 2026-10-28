# Lombard Sezam — kontynuacja pracy

Repozytorium: **angsm111-dot/lombard-11**, `main`. Firma: **Lombard Sezam**; Lombard 11 to tylko nazwa projektu/domeny. Adres: Pocztowa 11, 66-400 Gorzów Wielkopolski; tel./WhatsApp 601 775 146. Nie twórz kolejnych projektów.

Właściciel upoważnił do wykonywania zleconych poprawek, commitów, push i publikowania zaakceptowanego zakresu na JDM bez zgody przy każdej aktualizacji. Zezwolił też na usunięcie WordPressa. Nie zmieniaj poczty, innych domen ani nie usuwaj baz i backupów bez osobnej dyspozycji. Nie korzystaj z danych dostępowych/katalogów/skryptów projektu lombard-gorzow.pl.

## Codzienna aktualizacja

1. Edytuj `templates/`, `dist/data/` lub właściwe pliki statyczne. Uruchom `python3 scripts/build.py` i `python3 scripts/jdm/check_site.py`. `dist/` jest śledzony w Git. Zmiany wyglądu sprawdź mobilnie i na desktopie.
2. Zapisz zmiany na GitHubie w `main`. `.github/workflows/jdm.yml` automatycznie buduje, sprawdza i publikuje **podgląd oraz produkcję na JDM**. Nie trzeba ręcznie kopiować plików. Nie uruchamiaj publikacji innymi, historycznymi skryptami.
3. Odczytaj na gałęzi **jdm-status**: `latest.json`, `jdm-production.json`, `jdm-preview.json` oraz historię `runs/`. Sukces wymaga `state=verified`, `public_verified=true` i zgodności pełnego SHA commita. Sam push ani zielona budowa nie oznaczają publikacji.
4. Błędy odczytuj z Actions runa wskazanego w statusie, przez narzędzia GitHuba. Nie proś właściciela o kolejne screeny logów. Nie drukuj sekretów.

## Aktualna infrastruktura, potwierdzona 28.10.2026

- Produkcja **https://lombard11.pl/**, także dostęp przez www; canonical HTML wskazuje domenę bez www. Nie twierdź, że jest przekierowanie 301 www: po odejściu od WP publiczna odpowiedź www to 200.
- Automatyczny podgląd JDM **https://lombard11.pl/podglad-sezam11/**. Pełna wersja, linki z prefiksem, noindex. Podgląd jest publiczny; noindex nie chroni dostępu.
- Dotychczasowy osobny podgląd Sites https://lombard-11.angsm111.chatgpt.site pozostaje prywatny. Nie zmieniaj jego odbiorców.
- SSH `web15.jdm.pl:2233`, konto `lombardp`; dane ustalone z panelu i rzeczywistego logowania dla tego projektu.
- Konto `/home/lombardp`; właściwy document root `/home/lombardp/public_html` potwierdzony przez SSH i własny losowy plik odczytany z publicznej domeny.
- Bazy wersji `.sezam11-production` oraz `.sezam11-preview` w tym koncie. `public_html` jest zarządzanym dowiązaniem do `.sezam11-production/current`; podgląd ma własny `current`.
- Transport **php-static**: `scripts/jdm/php_deploy.py`, `remote.php`, `package.py`, konfiguracja `hosting/jdm.json`. PHP 7.4+ służy tylko przez CLI do publikacji; strona działa statycznie bez WP/PHP. Serwer nie ma Pythona.
- Pełne archiwum SCP, SHA-256 archiwum i każdego pliku, dokładny zestaw plików, odrzucanie niebezpiecznych ścieżek/dowiązań. Jedyny dozwolony dodatkowy link w wersji produkcyjnej to dokładny adres podglądu. Bez rsync i automatycznego sprzątania wersji.
- Pierwszy cutover przeniósł WP do `.sezam11-wordpress-backup-aa59bb5025788e7095bbad2bd0dc0ef41959c587` poza publicznym rootem. Baza i backupy niezmienione. Nie przywracaj WP jako wymogu kolejnych aktualizacji.

## Dostęp i zabezpieczenia

Hasło jest wyłącznie w GitHub Secret `JDM_SSH_PASSWORD`. Publiczny klucz hosta w `hosting/ssh_known_hosts`, fingerprint w konfiguracji. Właściciel polecił 28.10 kontynuować bez BOK: klucz przypięty przy pierwszym użyciu (TOFU), **bez niezależnej weryfikacji**. Nie odświeżaj go automatycznie, nie używaj `StrictHostKeyChecking=no`. Przy zmianie klucza przerwij i ustal przyczynę.

Workflow ma wspólną kolejkę bez anulowania, serwerowy flock i bash z pipefail. Zmiany zasobów mają wersję commita w URL; publiczna kontrola sprawdza HTML, metadane commita, odpowiedzi HTTP i checksumy CSS/JS/logo. Nie wyłączaj walidacji TLS.

**SSL originu/Cloudflare Full (strict) właściciel odłożył na później. Nie zmieniaj go teraz.** Publiczne HTTPS działa przez Cloudflare; nie potwierdza to certyfikatu JDM ani trybu strict. **Nowsze polecenie właściciela:** po migracji włączyć zaślepkę na produkcji i zachować pełny podgląd. `maintenance_enabled=true` w hosting/jdm.json jest teraz trwałym ustawieniem produkcji. Każdy zwykły deploy zachowuje zaślepkę (HTTP 503 + Retry-After), a podgląd zawsze publikuje pełną stronę. Na polecenie „wyłącz przerwę” zmień wyłącznie tę flagę na false, zrób commit/push i sprawdź HTTP 200 oraz commit. Nie zdejmuj zaślepki przy zwykłych poprawkach. Opcje on/off usunięto z workflow; zmiana jest wersjonowana przez tę flagę, nie jednorazowy runtime override.

## Treść strony

Zachowaj osobne podstrony, aktualne menu, unikalne zdjęcia 11 artykułów i zatwierdzony spektrometr. OLX: https://www.olx.pl/oferty/uzytkownik/G2XGE/. Ceny odczytywane z istniejącego publicznego API, bez ponownego naliczania marży i bez zmian panelu admina. Archiwalne wpisy WP nie zostały przeniesione do nowej strony; inwentaryzacja i backup pozostają dostępne do oddzielnej migracji SEO.

Pełna instrukcja: `docs/JDM.md`. Historyczne `remote.py`, wzorce Nginx, Apache i bridge nie są aktualną ścieżką wdrożenia.
