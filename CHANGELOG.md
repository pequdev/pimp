# Changelog

Wszystkie istotne zmiany w aplikacji będą dokumentowane w tym pliku.

## [1.12.0] - 2024-09-06
### Nowe funkcjonalności:
- **Usprawnione zarządzanie wirtualnym środowiskiem**: Dodano nowe komendy do `Makefile`, które umożliwiają pełną automatyzację tworzenia, aktualizacji i wchodzenia w środowisko wirtualne. Nowa komenda `make update_venv` pozwala na odświeżenie środowiska po aktualizacji `requirements.txt`, a `make activate_venv` ułatwia wejście do środowiska.
- **Wykrywanie i przypisywanie stron domowych**: Zaktualizowano algorytm wyszukiwania stron domowych restauracji. System teraz lepiej rozpoznaje strony na podstawie porównania domeny z nazwą restauracji, co umożliwia bardziej precyzyjne przypisanie odpowiednich stron do kolumny `Website`.
- **Poprawione logowanie**: Usprawniono dynamiczne raportowanie zadań asynchronicznych za pomocą bibliotek `rich.console` oraz `rich.live`. Logowanie w czasie rzeczywistym prezentuje wyniki przetwarzania z większą szczegółowością i lepszą czytelnością.
- **Wprowadzenie obsługi wyjątków**: Zaimplementowano zaawansowane obsługi błędów w procesie przetwarzania danych społecznościowych i godzin otwarcia. Program lepiej radzi sobie z nieprzewidzianymi sytuacjami, zapewniając stabilność działania.

## [1.11.0] - 2023-09-06
### Nowe funkcjonalności:
- **Automatyczne dopasowanie stron domowych na podstawie nazwy restauracji**: Wprowadzono mechanizm, który sprawdza, czy host strony zawiera fragment nazwy restauracji, a następnie przypisuje stronę do kolumny `Website`. Dzięki temu dokładniej identyfikowane są rzeczywiste strony domowe.
- **Usprawnione przetwarzanie linków społecznościowych**: Linki z serwisów takich jak Instagram, Facebook, YouTube, TripAdvisor i TheFork są teraz automatycznie przypisywane do odpowiednich kolumn, co poprawia dokładność danych w pliku CSV.
- **Nowa metoda filtrowania stron domowych**: Zaimplementowano dodatkowy warunek w metodzie `is_potential_website`, który wyklucza linki zawierające domeny serwisów społecznościowych i recenzji (np. `tripadvisor.com`, `thefork.com`), umożliwiając lepsze rozdzielenie stron domowych od platform recenzji.
- **Lepsza integracja z konsolą**: Zaktualizowano logikę raportowania, aby precyzyjniej wyświetlać informacje o przetwarzaniu danych społecznościowych i stron domowych w czasie rzeczywistym w konsoli, z wykorzystaniem `rich.console` i `rich.table`.
- **Obsługa wyszukiwań w Google**: Ulepszono mechanizm wyszukiwania w Google, umożliwiając bardziej precyzyjne i dynamiczne pobieranie danych na podstawie wyników wyszukiwania, z zachowaniem odpowiedniego rozdzielenia platform społecznościowych i stron domowych.

## [1.10.0] - 2023-09-06
### Nowe funkcjonalności:
- **Automatyczne przypisywanie stron domowych**: Dodano funkcjonalność, która automatycznie wykrywa i przypisuje strony domowe restauracji do kolumny `Website`. System rozpoznaje strony platform społecznościowych i serwisów recenzji, takich jak TripAdvisor, TheFork, Yelp, i przypisuje je do odpowiednich kolumn, zamiast klasyfikować je jako strony domowe.
- **Obsługa nowych kolumn dla recenzji**: Linki z serwisów recenzji (TripAdvisor, TheFork) są teraz automatycznie przypisywane do odpowiednich kolumn, co umożliwia lepsze rozdzielenie danych w pliku CSV.
- **Dynamiczne wyszukiwanie i raportowanie**: Ulepszono dynamiczne wyszukiwanie i raportowanie w czasie rzeczywistym, w tym wyświetlanie wyników przetwarzania linków społecznościowych i stron domowych z wyraźnym rozdzieleniem danych w konsoli.

### Poprawki:
- **Lepsze zarządzanie brakującymi danymi**: W przypadku braku wyników wyszukiwania dla danej platformy lub strony domowej, przypisywana jest pusta wartość (`""`) zamiast `0`, co poprawia czytelność pliku wyjściowego.
- **Poprawione wykluczanie serwisów recenzji z kolumny `Website`**: Linki do TripAdvisor, TheFork, Yelp i innych serwisów recenzji są teraz prawidłowo wykluczane z kolumny `Website`, co eliminuje przypadkowe przypisanie tych stron jako stron domowych.

## [1.9.0] - 2023-09-06
### Nowe funkcjonalności:
- **Przetwarzanie godzin otwarcia**: Dodano funkcjonalność do przetwarzania i pobierania godzin otwarcia z profili Google dla lokali gastronomicznych. Wyniki są zapisywane w kolumnie `Hours` jako string w formacie JSON, z rozbiciem na dni tygodnia.
- **Ulepszone logowanie i raportowanie**: Wprowadzono ujednolicone logowanie operacji za pomocą `rich.console`, w tym raportowanie statusu przetwarzania zarówno danych społecznościowych, jak i godzin otwarcia.
  
### Poprawki:
- **Refaktoryzacja klasy `Scraper`**: Ujednolicono sposób inicjalizacji i zamykania WebDrivera oraz wprowadzono obsługę parsowania HTML za pomocą BeautifulSoup. Dodano bezpieczne zarządzanie sesjami przeglądarki.
- **Optymalizacja klasy `Process`**: Zaimplementowano obsługę cache dla danych społecznościowych i godzin otwarcia, co przyspiesza ponowne przetwarzanie zapytań. Dodano automatyczne tworzenie kolumny `SocialData`, jeśli nie istnieje.
- **Poprawa obsługi cache**: W klasie `Cache` wprowadzono obsługę błędów odczytu/zapisu pliku cache oraz dodano logowanie operacji zapisu i ładowania cache, co usprawnia śledzenie stanu danych.
  
## [1.8.0] - 2023-09-06
### Nowe funkcjonalności:
- **Drzewo wyników wyszukiwania na żywo**: Ulepszono dynamiczne wyświetlanie wyników w czasie rzeczywistym, w tym strukturę drzewa HTML i pięć pierwszych wyników wyszukiwania Google dla każdej restauracji. Teraz użytkownicy mogą obserwować drzewo wyników, które jest wyświetlane natychmiast po przetworzeniu każdego zapytania.
- **Historia wyników w drzewie**: Dodano funkcję, która wyświetla historię przetwarzanych zapytań w formie drzewa, zamiast wyświetlania tylko ostatniego wyniku po zakończeniu operacji.
  
### Poprawki:
- **Poprawki w renderowaniu tabeli statusu**: Ulepszono sposób, w jaki tabela z zadaniami asynchronicznymi jest renderowana w konsoli z użyciem `rich.live`. Poprawiono równomierne rysowanie tabeli i jej aktualizację, aby wyniki były bardziej czytelne.

## [1.7.0] - 2023-09-06
### Nowe funkcjonalności:
- **Filtrowanie śmieci z linków społecznościowych**: Zaimplementowano automatyczne usuwanie niepotrzebnych parametrów (np. `?hl=en`, `?locale`) z wyników wyszukiwania Google dla linków społecznościowych.
- **Ulepszone budowanie zapytań**: Teraz zapytania Google są budowane na podstawie zarówno nazwy knajpy, jak i jej lokalizacji, co poprawia trafność wyników.

### Poprawki:
- **Testy jednostkowe i integracyjne**: Zaktualizowano testy jednostkowe, aby bardziej realistycznie odwzorowywały strukturę danych w CSV oraz lepiej testowały logikę aplikacji, w tym wyszukiwanie wielu platform.
- **Poprawki obsługi wyjątków**: Ulepszono obsługę wyjątków przy zapisie pliku wynikowego, eliminując błędy związane z tworzeniem katalogów.

## [1.6.0] - 2023-09-05
### Nowe funkcjonalności:
- **Asynchroniczne przetwarzanie brakujących danych**: Dodano funkcję `process_missing_data`, która obsługuje brakujące dane asynchronicznie i pozwala na dynamiczne monitorowanie postępu.
- **Wyszukiwanie profili społecznościowych**: Aplikacja automatycznie uzupełnia brakujące linki do profili społecznościowych (Instagram, TikTok, Facebook, YouTube, TripAdvisor, TheFork) na podstawie wyników wyszukiwania Google.
- **Rozszerzone logowanie z flagą verbose**: Dodano szczegółowe logowanie z użyciem `verbose`, które wyświetla informacje o strukturze strony i wyniki wyszukiwania w czasie rzeczywistym.

## [1.5.0] - 2023-09-05
### Nowe funkcjonalności:
- **Mockowanie `pandas.read_csv` w testach CLI**: Użyto `unittest.mock` do mockowania funkcji `pandas.read_csv` w testach CLI, aby wyeliminować zależność od fizycznych plików CSV.
- **Mockowanie `process_missing_data`**: Zmockowano funkcję `process_missing_data` w testach CLI, aby umożliwić kontrolowane testowanie wyników bez rzeczywistego przetwarzania danych.
- **Poprawki w testach CLI**: Testy CLI zostały zaktualizowane, aby działały poprawnie bez wymogu posiadania pliku `data/test.csv`.

### Poprawki:
- Usunięto zależność od pliku `data/test.csv` w testach CLI.
- Zoptymalizowano testy CLI poprzez użycie mockowania, co pozwala na bardziej niezależne testowanie aplikacji bez fizycznych danych.

## [1.4.0] - 2023-09-05
### Nowe funkcjonalności:
- **Dynamiczne monitorowanie zadań asynchronicznych**: Dodano progres bar do monitorowania postępu przetwarzania danych w czasie rzeczywistym.
- **Nowe funkcje CLI**: Informacje o błędach są dynamicznie wyświetlane podczas działania aplikacji.
- **Poprawki wizualne**: Zastosowanie bardziej rozbudowanych komunikatów z użyciem kolorów, ikon sukcesu, ostrzeżeń i błędów.
- **Dokumentacja**: Dodano plik `README.md` z instrukcją instalacji, uruchamiania aplikacji oraz opisem opcji CLI.

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