# Automatyczna publikacja na JDM — Lombard Sezam

## Stan działający (28 października 2026)

- Repozytorium: https://github.com/angsm111-dot/lombard-11, gałąź `main`.
- Produkcja: **https://lombard11.pl/**.
- Podgląd JDM: **https://lombard11.pl/podglad-sezam11/**, pełna wersja z noindex i własnymi linkami. Jest publiczny; noindex nie jest hasłem.
- Starszy prywatny podgląd Sites: https://lombard-11.angsm111.chatgpt.site — zachowany bez zmiany dostępu. Workflow JDM nie aktualizuje tego dodatkowego podglądu Sites.
- Pierwsza produkcja: commit `aa59bb5025788e7095bbad2bd0dc0ef41959c587`, [udane wdrożenie](https://github.com/angsm111-dot/lombard-11/actions/runs/40733749753). Przesłano i potwierdzono 63 pliki produkcyjne. Podgląd sprawdzono też w przeglądarce przy szerokościach 390 i 1440 px.

## Co robi Codex po kolejnej poprawce

1. Zmienia pliki w tym projekcie, uruchamia generator i właściwe kontrole.
2. Zapisuje commit i wysyła go na `main` GitHuba. Nie wymaga osobnego potwierdzenia publikacji zleconych zmian.
3. GitHub Actions (`.github/workflows/jdm.yml`) buduje stronę, sprawdza linki, obrazy i testy publikacji. Następnie publikuje najpierw podgląd, potem produkcję.
4. Codex odczytuje wynik na gałęzi `jdm-status` oraz faktyczny numer commita na publicznej stronie. Nie traktuje samego push ani zielonej budowy jako sukcesu publikacji.

Budowa: `python3 scripts/build.py`; kontrola: `python3 scripts/jdm/check_site.py`; testy transportu: `python3 -m unittest discover -s tests -v`. Runner instaluje PHP CLI do testów aktualnego backendu. `dist/` jest śledzony w repozytorium; paczki powstają w ignorowanym `build/` i nie zawierają sekretów.

## Faktyczne ścieżki i serwer

Dane ustalono od nowa z panelu właściciela i rzeczywistego SSH, bez kopiowania dostępu z lombard-gorzow.pl:

| Element | Potwierdzona wartość |
|---|---|
| Serwer SSH | `web15.jdm.pl` |
| Port | `2233` |
| Użytkownik | `lombardp` |
| Katalog konta | `/home/lombardp` |
| Document root | `/home/lombardp/public_html` |
| Wersje produkcji | `/home/lombardp/.sezam11-production/releases/` |
| Aktywna produkcja | `/home/lombardp/.sezam11-production/current` |
| Wersje podglądu | `/home/lombardp/.sezam11-preview/releases/` |
| Aktywny podgląd | `/home/lombardp/.sezam11-preview/current` |

Przypisanie domeny do document root potwierdzono własnym losowym plikiem testowym odczytanym przez publiczne HTTPS **przed przygotowaniem katalogów**. `public_html` jest obecnie dowiązaniem do aktywnej produkcji. W każdej wersji produkcyjnej jest jedno kontrolowane dowiązanie `podglad-sezam11` do aktywnego podglądu. Nginx obsługuje statyczne pliki i dowiązania, co potwierdziły testy publiczne.

Serwer nie ma Pythona; ma PHP i SCP. Aktualny transport: **php-static**, skrypty `scripts/jdm/php_deploy.py`, `remote.php`, `package.py`. PHP działa przez CLI przy wdrożeniu. Sama nowa strona nie potrzebuje PHP ani WordPressa. Nie potrzeba nowego vhosta ani niestandardowej konfiguracji Nginx. JDM ignoruje `.htaccess`; wcześniejsze wzorce Apache/Nginx i bridge nie są instalowane.

## Dokładne sekrety

Miejsce: https://github.com/angsm111-dot/lombard-11/settings/secrets/actions → **New repository secret**.

| Nazwa | Znaczenie |
|---|---|
| `JDM_SSH_PASSWORD` | Jedyny wymagany sekret aktualnego transportu: hasło SSH z panelu JDM, już zapisane przez właściciela. |
| `JDM_SSH_KNOWN_HOSTS` | Opcjonalne nadpisanie publicznego klucza hosta; musi pasować do przypiętego fingerprintu. Domyślnie używany jest publiczny plik `hosting/ssh_known_hosts`. |

Klucz publiczny serwera nie jest tajnym kluczem prywatnym ani hasłem. Host/port/login nie są sekretami i znajdują się w konfiguracji potwierdzonego konta. Starsze opcjonalne sekrety `JDM_SSH_HOST`, `JDM_SSH_PORT`, `JDM_SSH_USER`, `JDM_SSH_PRIVATE_KEY` dotyczą historycznego backendu; nie są wymagane i nie sterują aktywnym php-static. Nie trzeba ich dodawać. `GITHUB_TOKEN` jest dostarczany automatycznie i służy tylko do statusów; nie dodawać go ręcznie.

Hasło przekazywane przez `sshpass -e`, nigdy argumentem polecenia. Nie zapisujemy go do repozytorium, plików paczki ani logów. Nie włączać `set -x`. Nie generować nowego hasła w JDM bez potrzeby. Zmiana hasła wymaga aktualizacji tylko `JDM_SSH_PASSWORD`.

Produkcję/podgląd włączają `production_enabled` i `preview_enabled` w `hosting/jdm.json`. Można je nadpisać zwykłymi GitHub Variables `JDM_PRODUCTION_ENABLED` i `JDM_PREVIEW_ENABLED` w zakładce Variables (nie Secrets); `false` wyłącza odpowiedni cel. Brak zmiennej oznacza użycie konfiguracji z repozytorium.

## SSH: przypięcie przy pierwszym połączeniu

Właściciel polecił kontynuować bez potwierdzenia BOK. Przypięto początkowy klucz ED25519 odczytany podczas audytu:

`SHA256:maeVhAooEo6C8SFZn4FP2u5Kz+kOkgxQaw7lvJql8Qc`

To **trust-on-first-use**, nie niezależne potwierdzenie tożsamości. Ten fakt zapisano w konfiguracji. `StrictHostKeyChecking=yes` i kontrola SHA-256 pozostają włączone. Nowy wynik `ssh-keyscan` nie aktualizuje zaufanego klucza. Przy zmianie klucza wdrożenie ma się zatrzymać do ustalenia przyczyny.

## Transfer i kontrola

- Jedna kolejka workflow dla projektu, `cancel-in-progress: false`; dodatkowo `flock` na serwerze.
- Bash `-euo pipefail`: logowanie przez `tee` nie ukrywa błędów.
- Pełna paczka SCP przez SSH, bez rsync i bez kopiowania przyrostowego.
- SHA-256 archiwum i każdego pliku, dokładny zestaw plików, odrzucanie duplikatów nazw, ścieżek poza katalogiem i dowiązań z archiwum.
- Nowy katalog `releases/COMMIT-RUN-ATTEMPT`; aktywacja przez zamianę dowiązania `current`. Brak automatycznego usuwania starych wersji.
- Pełny SHA commita w `deployment.json` oraz HTML. Wszystkie lokalne CSS/JS/obrazy mają wersję commita w URL.
- Publiczna kontrola HTTPS strony głównej, kontaktu, bloga i oferty, zgodności commita oraz checksumów CSS/JS/logo. Produkcja sprawdza też HTTP 404 dla nieznanego adresu. Nie wyłączamy walidacji TLS.
- Przy błędzie próba przywrócenia poprzedniego `current`. Błąd cofania jest jawnie raportowany, nie zamieniany w sukces. Przy pierwszym cutoverze można przywrócić zachowany katalog WP.

## Statusy bez kolejnych screenów

Gałąź https://github.com/angsm111-dot/lombard-11/tree/jdm-status zawiera:

- `latest.json`: ostatni run, etap, wynik, pełny commit, link do Actions;
- `jdm-production.json` i `jdm-preview.json`: ostatnie pomyślne wyniki danego celu;
- `runs/RUN-ATTEMPT.json`: historia każdego uruchomienia;
- `jdm-audit.json`: publiczny DNS/TLS i niezweryfikowany odczyt kluczy;
- `jdm-inspection.json`: wcześniejszy potwierdzony odczyt SSH.

`verified` + `public_verified=true` + zgodność SHA oznaczają potwierdzone wdrożenie. `failed` oznacza błąd; `awaiting_configuration` brak aktywnego celu. Jeśli run zawiedzie, ostatni poprawny plik per-target może być starszy — trzeba porównać commit z `latest.json` i Actions. Szczegóły błędów Codex odczytuje przez narzędzia Actions z podanego runa, bez żądania screenshotów od właściciela.

## WordPress i cofnięcie pierwszego przełączenia

Właściciel wyraźnie zezwolił na usunięcie WP. Zamiast kasować pliki podczas przełączenia zachowano pełny katalog w:

`/home/lombardp/.sezam11-wordpress-backup-aa59bb5025788e7095bbad2bd0dc0ef41959c587`

Jest poza publiczną stroną; WordPress nie obsługuje już domeny. Baza, snapshoty, inne domeny i poczta niezmienione. Własny plik `legacy-root.json` wskazuje tę kopię. Przywrócenie katalogu wymaga świadomego cofnięcia migracji; zwykły deploy wraca do poprzedniej wersji statycznej. Nie kasować baz i kopii bez osobnego polecenia.

Stare wpisy WordPressa nie zostały automatycznie zaimportowane do nowego bloga. Inwentaryzacja dawnych adresów jest w `hosting/legacy-url-inventory.csv`; eksport publicznych treści i zachowany WP pozwalają przygotować oddzielną migrację SEO. Nowa strona zawiera 11 artykułów.

## SSL odłożony; przerwa aktywowana na nowsze polecenie

Zgodnie z poleceniem właściciela nie zmienialiśmy certyfikatów ani trybu Cloudflare. Po udanym przełączeniu właściciel zlecił zaślepkę na produkcji, z pełną stroną podglądu do dalszych poprawek. Publiczne HTTPS działa przez Cloudflare: audyt widzi certyfikat Google Trust Services dla lombard11.pl i *.lombard11.pl. Panel JDM pokazywał brak certyfikatu originu. Nie oznacza to potwierdzenia Full (strict); ten wymaga osobnego testu certyfikatu JDM/SNI i odczytu ustawienia Cloudflare.

Sterowanie zaślepką: `maintenance_enabled` w `hosting/jdm.json`. `true` publikuje na produkcji wyłącznie zaślepkę i minimalne pliki, **HTTP 503**, `Retry-After: 300`, no-store, noindex. Strony HTML i dane artykułów pełnej wersji nie są publikowane w tej paczce. Nowy backend PHP nie uruchamia WP; mały własny index.php odpowiada za właściwy kod 503. Podgląd zawsze otrzymuje pełne HTML, obrazy i blog, niezależnie od tej flagi. Zwykłe poprawki i push nie zdejmują zaślepki.

Włączenie/wyłączenie właściciel zleca tutaj w Codexie. Codex zmienia flagę na true/false, robi commit/push i sprawdza publiczny kod 503/200 oraz commit. Nie ma potrzeby kopiowania plików ani logowania do panelu. Flaga jest wersjonowana w GitHubie; opcje jednorazowe on/off usunięto z workflow, aby następny push nie nadpisywał przypadkowo decyzji. Przy wyłączeniu pełna statyczna wersja wraca przez nowy release bez usuwania kopii WP.

Wersja www działa, ale po odejściu od WP zwraca 200, nie dawny redirect WordPressa. Canonical w HTML wskazuje https://lombard11.pl. Ewentualny redirect serwerowy www i finalną konfigurację SSL można wykonać w panelu/Cloudflare, bez zmiany poczty.
