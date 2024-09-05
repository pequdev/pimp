---

### Zaktualizowany `CHANGELOG.md`

Dodajemy nową wersję z uwzględnieniem najnowszych zmian dotyczących README i dynamicznego monitorowania.

```markdown
# Changelog

Wszystkie istotne zmiany w aplikacji będą dokumentowane w tym pliku.

## [1.4.0] - 2023-09-05
### Nowe funkcjonalności:
- **Dynamiczne monitorowanie zadań asynchronicznych**:
  - Dodano progres bar do monitorowania postępu przetwarzania danych w czasie rzeczywistym.
  - Wprowadzenie dynamicznej tabeli, która śledzi status zadań `asyncio` i informuje o zakończonych zadaniach oraz błędach.
- **Nowe funkcje CLI**:
  - Informacje o błędach są dynamicznie wyświetlane podczas działania aplikacji.
  - Lepsza wizualizacja procesów przy użyciu `rich.live`, `Progress` i ikon emoji.
- **Poprawki wizualne**:
  - Zastosowanie bardziej rozbudowanych komunikatów z użyciem kolorów, ikon sukcesu, ostrzeżeń i błędów.
- **Dokumentacja**:
  - Dodano plik `README.md` z instrukcją instalacji, uruchamiania aplikacji oraz opisem opcji CLI.

## [1.3.0] - 2023-09-05
### Nowe funkcjonalności:
- Dodano testy jednostkowe i integracyjne przy użyciu Pytest.
- Wprowadzono mockowanie zapytań Google, aby umożliwić testowanie bez rzeczywistych zapytań.
- Testy CLI z Click, sprawdzające różne scenariusze wywołania aplikacji (np. brak flagi `--social`).

## [1.2.0] - 2023-09-03
### Nowe funkcjonalności:
- Wprowadzono pełną obsługę CLI z użyciem Click.
- Dodano flagę `--social` do aktywacji uzupełniania profili społecznościowych.
- Dodano flagę `--verbose`, umożliwiającą szczegółowe logowanie operacji w trakcie przetwarzania danych.
- Przy braku flagi `--social`, aplikacja wyświetla komunikat o braku wybranej funkcji oraz standardowy help.

## [1.1.0] - 2023-09-01
### Nowe funkcjonalności:
- Dodano mechanizm cache, aby uniknąć ponownych zapytań Google i przyspieszyć przetwarzanie.
- Dodano obsługę wyjątków: gdy brak wyników Google dla danej domeny, wartość w CSV ustawiana jest na `-1`.

## [1.0.0] - 2023-08-30
### Pierwsza wersja:
- Podstawowa funkcjonalność aplikacji:
  - Wczytywanie pliku CSV.
  - Asynchroniczne wyszukiwanie danych w Google dla brakujących profili.
  - Filtrowanie wyników po domenach (Instagram, TikTok, Facebook, itd.).
  - Zapisywanie wyników do CSV.