# Lombard 11 — Sezam

Pierwszy projekt strony informacyjnej lombardu. Responsywna strona statyczna w HTML, CSS i JavaScript, bez zależności wykonawczych.

## Podgląd lokalny

```sh
python3 -m http.server 8000 --directory dist
```

## Zawartość

- Skup złota z tabelą prób. Brak potwierdzonych stawek: strona kieruje do kontaktu, nie wyświetla wymyślonych cen.
- Informacja o badaniu spektrometrem.
- Kategorie przyjmowanych przedmiotów.
- Bezpośredni link do oferty OLX Sezam.
- Kontakt i pływający przycisk WhatsApp.
- Trzy poradniki z osobnymi adresami, zapisane jako uporządkowane dane.

## Przyszły system publikacji

Źródło artykułów: `dist/data/articles.json`. Każdy wpis ma stabilne `id`, `slug`, kategorię, zajawkę i sekcje tekstowe. Integracja z centralnym systemem CMS nie jest jeszcze wykonana. Po zmianie danych uruchom `python3 scripts/build.py`, aby wygenerować strony wpisów. Strona główna pobiera listę z tego samego pliku. Treści są escapowane przy generowaniu i renderowane przez textContent w przeglądarce.

## Dane i zasoby

Dane kontaktowe potwierdzone przez właściciela: Pocztowa 11, Gorzów Wielkopolski; telefon i WhatsApp 601 775 146. Logo pobrane z sezam.com.pl na prośbę właściciela. OLX: https://www.olx.pl/oferty/uzytkownik/G2XGE/. Zdjęcie biżuterii wygenerowane na potrzeby projektu; nie przedstawia rzeczywistego stanu magazynowego.

## Do uzupełnienia

Potwierdzone stawki skupu, ewentualny koszt badania, pełna informacja o prywatności i umowa API z przyszłym CMS. Publikacja Sites jest prywatna do czasu zmiany dostępu przez właściciela.
