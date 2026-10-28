# Lombard Sezam / lombard-11

Pracuj w istniejącym `angsm111-dot/lombard-11`, `main`. Nazwa firmy: **Lombard Sezam**; `lombard11.pl` to domena. Nie twórz kolejnych projektów. Właściciel upoważnił do poprawek, commitów, push i publikacji zaakceptowanego zakresu bez każdorazowej zgody.

## Budowa i kontrola

- Statyczne strony: `templates/`, `dist/data/`, `scripts/build.py`; `dist/` jest również śledzony w Git.
- Uruchom `python3 scripts/build.py`, `python3 scripts/jdm/check_site.py` oraz `python3 -m unittest discover -s tests -v` dla zmian publikacji. Dla zmian wyglądu sprawdź też mobilne menu/podgląd.
- Ceny odczytuj gotowe z istniejącego API; nie naliczaj marży drugi raz. Nie zmieniaj panelu cen przy pracach nad hostingiem.
- Zachowaj osobne podstrony, unikatowe fotografie artykułów, aktualny link OLX i zatwierdzone zdjęcie spektrometru.

## JDM: najpierw fakty, potem publikacja

Czytaj `docs/JDM.md`, `hosting/jdm.json` i gałąź **jdm-status** (`latest.json`, pliki `jdm-production.json` / `jdm-preview.json`, historia `runs/`). Push NIE potwierdza publikacji. Sukces wymaga SHA-256 po SSH oraz sprawdzenia publicznego HTML i `deployment.json` z właściwym commitem, docelowym hostem i stanem przerwy.

Ustal dane tego projektu osobno. Nie kopiuj kluczy, katalogów, loginów, skryptów lub procedur czyszczenia z lombard-gorzow.pl. Nie odczytuj wartości sekretów. Nie zapisuj ich do repozytorium/logów. Brak danych oznacza `awaiting_configuration`, nigdy sukces wdrożenia.

JDM używa **Nginx i ignoruje .htaccess**. Wzorce Nginx muszą zostać dopasowane do potwierdzonych katalogów i wdrożone przez panel/BOK. Flaga `webserver_rules_verified` wymaga realnego testu, także HTTP 503 przy przerwie oraz 404. Nie zakładaj obsługi dowiązań ani Pythona na serwerze: potwierdź przy preflight.

Nie zmieniaj poczty, innych domen ani nie kasuj WordPressa, jego bazy, starych plików lub backupów. Używaj nowego, wyraźnie wydzielonego katalogu ze znacznikiem projektu, pełnych paczek SCP i atomowego przełączenia dowiązania `current`. Brak jakiegokolwiek automatycznego sprzątania starych wersji. Zachowaj archiwum starego bloga i mapę dawnych adresów.

Produkcja i podgląd mają odrębne katalogi/hosty. Przerwa techniczna tylko na produkcji, wyłącznie na jawne polecenie, nigdy automatycznie przy wdrożeniu. Zmiana flagi nie usuwa strony. Nie myl odziedziczonej przerwy WordPressa z nowym mechanizmem.

Cloudflare: publiczny certyfikat nie potwierdza certyfikatu JDM. Nie ogłaszaj Full (strict) dopóki certyfikat originu z SNI i tryb w panelu Cloudflare nie zostały sprawdzone. Nigdy `curl -k`, `StrictHostKeyChecking=no` ani automatyczne zaufanie do ssh-keyscan.

## Obecny stan początkowy (2026-10-28)

Repo i budowa potwierdzone; domena nadal pokazuje starego WordPressa. Screen JDM: `web15.jdm.pl:2233`, użytkownik `lombardp`, **Brak certyfikatu SSL**. Ścieżki, klucz hosta, uwierzytelnienie SSH, nowy podgląd JDM i konfiguracja Nginx niepotwierdzone. Bez aktywnej produkcji JDM. Istniejący prywatny podgląd Sites zachowaj: https://lombard-11.angsm111.chatgpt.site .
