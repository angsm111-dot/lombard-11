# Publikacja lombard11.pl na JDM

## Stan i granice konfiguracji — 28.10.2026

Repozytorium `angsm111-dot/lombard-11`, gałąź `main`, statyczna budowa `python3 scripts/build.py`, wynik `dist/`. Bez zależności npm. Utworzono `.github/workflows/jdm.yml`; push do main uruchamia budowę/kontrolę oraz, po uzupełnieniu dostępu i potwierdzeniu ścieżek, publikację. **Na początku obie publikacje są wyłączone**; udana budowa nie jest potwierdzeniem publikacji.

Właściciel potwierdził przez screenshot panelu: **web15.jdm.pl:2233**, konto **lombardp**. Nie są to dane przejęte z innego projektu. Panel pokazuje WordPress 6.7.10, PHP 7.4, brak certyfikatu originu i brak kopii roboczej. Publiczne `https://lombard11.pl` odpowiada przez Cloudflare, nadal stroną WordPress z przerwą techniczną. Baza, pliki WP, backupy i poczta nie zostały zmienione.

**Niepotwierdzone:** katalog domeny, wydzielone katalogi nowej produkcji/podglądu, hostname podglądu, klucz hosta SSH, autoryzacja, Python 3/tryb SCP/dowiązania na JDM, certyfikat JDM, tryb SSL Cloudflare, reguły Nginx. Nie ustawiaj pól `verified` na podstawie przypuszczenia.

## Dokładne sekrety GitHuba

Miejsce: https://github.com/angsm111-dot/lombard-11/settings/secrets/actions → **New repository secret**. Sekrety repozytorium, nie zwykłe Variables:

| Nazwa | Wartość dla tego projektu |
|---|---|
| `JDM_SSH_HOST` | `web15.jdm.pl` — potwierdzony w panelu |
| `JDM_SSH_PORT` | `2233` — potwierdzony w panelu |
| `JDM_SSH_USER` | `lombardp` — potwierdzony w panelu |
| `JDM_SSH_PASSWORD` | obecne hasło SFTP/SSH z panelu JDM; nie regenerować bez potrzeby |
| `JDM_SSH_KNOWN_HOSTS` | pełna linia `[web15.jdm.pl]:2233 ssh-ed25519 AAAA...`, zgodna z odciskiem potwierdzonym przez JDM/BOK |
| `JDM_SSH_PRIVATE_KEY` | opcjonalna alternatywa dla hasła: nowy klucz wyłącznie tego projektu, publiczna część dodana do authorized_keys tego konta |

Nie trzeba jednocześnie hasła i klucza: klucz ma pierwszeństwo. `sshpass -e` przekazuje hasło przez środowisko procesu, nigdy argument polecenia; nie używamy `set -x`. Pliki z kluczem/known_hosts mają tryb 0600 w tymczasowym katalogu runnera. `GITHUB_TOKEN` jest automatyczny, ze scoped `contents: write`, służy tylko do statusów. Nie dodawać go ręcznie. Nie przechowywać tajnych wartości w plikach projektu ani w wiadomościach.

Zwykłe **Variables** (ta sama sekcja, zakładka Variables): `JDM_PREVIEW_ENABLED` i `JDM_PRODUCTION_ENABLED`; dopiero po przygotowaniu celów ustawić odpowiednie na `true`. Brak wartości = wyłączone. Nie włączać produkcji przed preflight i zachowaniem starego WordPressa.

## Ustalenie ścieżek i uruchomienie

1. JDM → właściwa strona **lombard11.pl** → dane SFTP/SSH oraz konfiguracja domeny. Potwierdzić rzeczywisty dokument root przez panel/BOK i `pwd -P`, `realpath` po uwierzytelnieniu. Nie zakładać `public_html`, `/home/...` ani katalogów z innych projektów.
2. Wykonać snapshot/pełny backup plików i bazy starego WP (publiczny eksport wpisów nie wystarcza). Pozostawić starą instalację bez zmian; wskazać możliwość powrotu do jej katalogu.
3. Utworzyć **nowe, puste, niezależne** katalogi bazowe dla nowej produkcji i podglądu, poza starą instalacją i poza katalogami innych domen. Dla każdego utworzyć `.lombard11-deploy-root`, zawartość dokładnie:
   - produkcja: `{"project":"lombard-11","domain":"lombard11.pl","target":"production"}`
   - podgląd: `{"project":"lombard-11","domain":"lombard11.pl","target":"preview"}`
   Ten znacznik jest świadomym dopuszczeniem danego katalogu; nie tworzyć go w katalogu WP. Skrypt odmawia katalogów z WP, nie nadpisuje zwykłego katalogu `current` ani dowiązań poza `releases`.
4. Potwierdzone absolutne ścieżki wpisać w `hosting/jdm.json` jako `production_root`, `preview_root`, hostname jako `preview_url`. Potwierdzić `paths_verified_from_panel`. Nie publikować haseł w tym JSON. Katalog domeny ma wskazywać **potwierdzony ROOT/current**. Dopiero przełączenie domeny w panelu/BOK decyduje o nowej stronie; workflow nie edytuje DNS ani konfiguracji innych stron.
5. Potwierdzić fingerprint SHA-256 klucza serwera niezależnie z JDM (BOK/zweryfikowany panel), zapisać `ssh_host_fingerprint_sha256`. Dopasować ten klucz do `JDM_SSH_KNOWN_HOSTS`. Sam wynik `ssh-keyscan` NIE potwierdza tożsamości serwera; nie używać TOFU ani `StrictHostKeyChecking=no`.
6. **JDM używa Nginx i nie obsługuje .htaccess.** Poprosić BOK o zastosowanie reguł z `hosting/nginx-production.conf.example` i osobno `hosting/nginx-preview.conf.example`, po zastąpieniu znacznika rzeczywistą ścieżką. Nie wklejać całego przykładowego serwera ani nie zastępować konfiguracji TLS. Potwierdzić obsługę dowiązania `current`, try_files, HTTP 404/503, wyłączenie cache i noindex podglądu. Pole `webserver_rules_verified` oznacza faktyczny test konfiguracji, nie samo wysłanie zgłoszenia.
7. Włączyć najpierw `JDM_PREVIEW_ENABLED=true`, uruchomić Actions → **JDM build and deploy** → Run workflow → target=preview, operation=deploy. Pierwsza wersja bez poprzednika nie jest automatycznie kasowana po błędzie; zostaje do kontroli. Panel/BOK może po wgraniu pierwszej wersji przełączyć podgląd na `current` i ponowić kontrolę.
8. Ustawić certyfikat originu, potwierdzić właściwe przekierowania i zachowanie starego bloga (patrz `hosting/MIGRACJA.md`). Dopiero potem włączyć produkcję. Pierwsza zmiana katalogu domeny wymaga czynności w panelu/BOK. Nie usuwać starego WordPressa.

Dokumentacja JDM: [dlaczego .htaccess nie działa](https://jdm.pl/pomoc/baza-wiedzy/dlaczego-htaccess-nie-dziala/), [panel klienta](https://jdm.pl/pomoc/baza-wiedzy/przeglad-panelu-klienta/). Niestandardowe reguły Nginx uzgadnia się przez Zgłoszenia/BOK.

## Przebieg kolejnych aktualizacji

Po zleceniu zmiany Codex edytuje źródła, buduje i sprawdza stronę, zapisuje commit i wysyła na main. Actions:

- globalna kolejka `lombard-11-jdm`, bez przerywania trwającego wdrożenia;
- `bash -euo pipefail` także przy `tee`;
- budowa + sprawdzenie lokalnych linków/obrazów + testy wdrożenia;
- pełne archiwum wszystkich plików dla każdego celu, metadane pełnego SHA commita w HTML i `deployment.json`;
- pełny SCP przez przypięty SSH (**bez rsync**), kontrola SHA-256 archiwum i każdego pliku na serwerze, kontrola dokładnego zestawu plików i odrzucenie dowiązań/path traversal w tar;
- nowy niezmienny katalog `releases/COMMIT-RUN-ATTEMPT`, następnie atomowa zamiana dowiązania `current`; dodatkowo blokada `flock` po stronie serwera;
- TLS-zweryfikowane żądania publicznego `deployment.json`, strony głównej, kontaktu, bloga i oferty, z kontrolą SHA commita w każdej odpowiedzi, HTTP 200 lub 503 zgodnie z flagą przerwy;
- po niepowodzeniu kontroli publicznej próba powrotu do poprzedniego dowiązania, bez usuwania nowej lub starej wersji. Gdy brak poprzednika — wymagana kontrola pierwszej konfiguracji, nigdy usunięcie danych;
- zapis wyniku do gałęzi `jdm-status`, weryfikowanej osobno od `main`.

Przy każdym runie wykonywany jest również odczytowy audyt DNS, publicznego certyfikatu i `ssh-keyscan`. Wynik trafia do `jdm-audit.json` na gałęzi statusów. Odczytany klucz jest oznaczony jako **niezweryfikowany**; nigdy nie jest automatycznie dodawany do zaufanych.

Statusy `awaiting_configuration`, `failed`, `verified` mają różne znaczenia. `latest.json` zawiera commit, etap, wynik, link do runa i informację `public_verified`; `runs/` zachowuje historię. Osobne ostatnie poprawne wyniki są w `jdm-production.json` i `jdm-preview.json`. Szczegóły błędu odczytać przez GitHub Actions tools z runa, bez proszenia właściciela o screeny. Jeśli GitHub nie pozwoli zapisać workflow lub statusu, zgłosić konkretny błąd uprawnień, nie udawać działania.

## Podgląd i przerwa techniczna

Dotychczasowy niezależny prywatny podgląd: https://lombard-11.angsm111.chatgpt.site . Pozostaje aktywny i nie dziedziczy flagi JDM. Nie zmieniać jego dostępu. Automatyczny podgląd JDM będzie miał **osobny potwierdzony hostname i root**; każdy push buduje pełną stronę podglądu. `noindex` nie jest ochroną dostępu; Basic Auth/ograniczenie dostępu uzgodnić osobno w panelu.

Przerwa: Actions → JDM build and deploy → Run workflow → **target=production** → **maintenance-on** / **maintenance-off**. Tylko jawna dyspozycja właściciela; zwykłe deploy zachowuje dotychczasową flagę i nigdy jej nie włącza. Nginx sprawdza plik `ROOT/maintenance.enabled`, odpowiedź 503 + Retry-After, pełna wersja w podglądzie nadal widoczna. Wyłączenie usuwa wyłącznie tę flagę, nie stronę. Przerwa starego WP jest osobnym mechanizmem.

## Cloudflare i SSL: dwa połączenia

1. Przeglądarka → Cloudflare: publiczny curl z walidacją TLS działa; Cloudflare headers potwierdzają proxy. Certyfikat widziany z tej sesji może być terminowany przez proxy wykonawcze, więc nie jest dowodem certyfikatu JDM.
2. Cloudflare → JDM: panel właściciela pokazuje **Brak certyfikatu**. Ustalić origin IP z panelu, aktywować Let's Encrypt dla lombard11.pl i www na JDM, sprawdzić ważność, SAN i łańcuch z SNI, np. z runnera `curl --resolve lombard11.pl:443:CONFIRMED_ORIGIN_IP https://lombard11.pl/`. Dla Cloudflare Origin CA użyć oficjalnego zaufanego CA, nigdy `-k`.
3. Odczytać bieżący tryb SSL/TLS w panelu Cloudflare; dopiero po kontroli originu potwierdzić Full (strict). Publiczne 200 nie potwierdza strict. Nie zmieniać globalnego trybu strefy ani DNS innych usług w ciemno.
4. Cache Rule: ominąć cache dla właściwej domeny i hostname podglądu (szczególnie deployment.json, HTML i tryb 503); nie polegać wyłącznie na query stringu. Kontrola commita zatrzyma wdrożenie przy starej treści. Nie zmieniać MX/TXT/poczty.

[Cloudflare Full (strict): wymagania certyfikatu originu](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/).

## Uproszczony odczyt bez zgłoszenia do BOK

Po potwierdzeniu klucza SSH można uruchomić operation=inspect. Używa już zapisanego JDM_SSH_PASSWORD oraz przypiętego publicznego klucza; nie wymaga ścieżek wdrożenia, włączenia produkcji, SSL originu ani zmian Nginx. Odczytuje fizyczny katalog konta, realpath public_html (wskazanego jako standard przez oficjalną dokumentację JDM), obecność plików WP i dostępność narzędzi. Nie odczytuje wp-config.php, bazy ani nie zapisuje plików. Odczytany katalog jest kandydatem do powiązania z domeną, nie automatycznym potwierdzeniem document root. Prywatne ścieżki tylko w logu Actions, nie na publicznej gałęzi statusów.

Na polecenie właściciela z 28.10.2026 konfigurację SSL pozostawiamy na później. Nie stanowi to potwierdzenia Full (strict). Nie obniżać walidacji TLS w kontrolach publikacji.

## Decyzja właściciela: przypięcie przy pierwszym użyciu

28.10.2026 właściciel ponownie polecił kontynuować bez potwierdzania klucza przez BOK. Przypięto konkretny początkowy klucz ED25519 z audytu, odcisk SHA256:maeVhAooEo6C8SFZn4FP2u5Kz+kOkgxQaw7lvJql8Qc. Publiczny klucz jest w hosting/ssh_known_hosts; nie jest to sekret ani klucz prywatny. To trust-on-first-use, NIE niezależne potwierdzenie tożsamości. Nie odświeżać pliku automatycznie. StrictHostKeyChecking=yes pozostaje włączone. Sekret known_hosts i host/user/port są opcjonalnymi nadpisaniami; hasło pozostaje wyłącznie w GitHub Secrets. Do czasu skonfigurowania wdrożeń push uruchamia wyłącznie odczyt SSH obok budowy/audytu. Brak zmian strony. SSL i przerwa na koniec, zgodnie z poleceniem.
