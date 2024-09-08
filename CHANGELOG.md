### Changelog

Wszystkie istotne zmiany w aplikacji będą dokumentowane w tym pliku.

## [1.17.0] - 2024-09-09

### Nowe funkcjonalności:
- **Dynamiczne raportowanie i aktualizowanie statusu przetwarzania danych**: Wprowadzono pełną integrację klasy `Scraper` z biblioteką `rich.live`, umożliwiając dynamiczną aktualizację logów oraz tabeli statusu przetwarzania w czasie rzeczywistym. Każde zadanie, takie jak pobieranie godzin otwarcia czy wyszukiwanie profili społecznościowych, teraz natychmiast odświeża odpowiednie elementy tabeli.
- **Zautomatyzowana obsługa zgód cookies w różnych językach**: Zaimplementowano automatyczne wyszukiwanie i kliknięcie przycisków zgód na pliki cookies w Google Maps w językach: angielskim, niemieckim, polskim i hiszpańskim. To usprawnia proces pobierania godzin otwarcia w różnych regionach.
- **Optymalizacja procesu pobierania godzin otwarcia**: Dodano bardziej rozbudowaną obsługę wyjątków oraz wsparcie dla sortowania godzin otwarcia w różnych językach (PL, EN, DE, ES). System teraz lepiej radzi sobie z interpretacją formatu godzin i ich sortowaniem od poniedziałku do niedzieli.

### Poprawki błędów:
- **Poprawiona aktualizacja statusu w tabeli**: Rozwiązano problem, w którym tabela nie odświeżała statusu zadania po zakończeniu pobierania danych. Teraz każda zmiana statusu, jak również komunikaty błędów, są natychmiastowo wyświetlane w tabeli.
- **Zwiększona stabilność działania WebDrivera**: Dodano lepsze zarządzanie instancjami WebDrivera, w tym bezpieczne zamykanie sesji po zakończeniu przetwarzania.

## [1.16.0] - 2024-09-08
#### Nowe funkcjonalności:
- **Możliwość wyboru konkretnego arkusza Google**: Dodano opcję `--sheet_name`, która pozwala użytkownikowi na wybranie konkretnego arkusza w pliku Google Sheets, z którym aplikacja ma pracować.
- **Tworzenie nowego arkusza `UPD/{oryginalna_nazwa_arkusza}`**: Przed zapisaniem danych aplikacja tworzy nowy arkusz o nazwie `UPD/{oryginalna_nazwa_arkusza}`, zamiast nadpisywać oryginalny arkusz, zapewniając tym samym większą elastyczność zarządzania danymi.
- **Rozszerzone logowanie autoryzacji w trybie verbose**: W trybie verbose dodano bardziej szczegółowe logowanie procesu autoryzacji Google Sheets, aby ułatwić debugowanie oraz śledzenie przebiegu autoryzacji.

## [1.15.0] - 2024-09-08
#### Nowe funkcjonalności:
- **Rozszerzona obsługa akceptacji Google Consent**: Dodano logikę umożliwiającą znalezienie przycisku zgody na pliki cookie na podstawie tekstu w różnych językach (EN, DE, PL, ES). System teraz szuka elementu `div` z odpowiednim tekstem i klika w jego element nadrzędny `button`, co zapewnia skuteczne akceptowanie zgód w różnych lokalizacjach językowych.
- **Dodanie logowania drzewa elementów `body` w trybie verbose**: W trybie verbose dodano funkcjonalność wyświetlania pełnej struktury drzewa elementów `body` przy użyciu BeautifulSoup. Dzięki temu użytkownik może zobaczyć pełną strukturę HTML załadowanej strony bezpośrednio w konsoli, co ułatwia debugowanie i analizę.
- **Usuwanie zbędnych fraz z godzin otwarcia**: Dodano mechanizm, który usuwa z tekstu godzin otwarcia niepotrzebne frazy, takie jak "Hide open hours" w różnych wersjach językowych, aby uzyskać czyste i poprawnie sformatowane dane.

#### Poprawki błędów:
- **Naprawa problemu z uruchamianiem WebDrivera w trybie headless na macOS**: Rozwiązano problem z uruchamianiem ChromeDrivera, który generował błąd `DevToolsActivePort file doesn't exist`. Dodano odpowiednie flagi konfiguracyjne (`--no-sandbox`, `--disable-dev-shm-usage`), co zapewnia poprawne działanie aplikacji w trybie headless.
- **Zwiększenie stabilności działania Google Consent**: Naprawiono błąd, w którym Selenium nie mogło poprawnie znaleźć i kliknąć przycisku zgody Google Consent. Teraz logika wyszukuje odpowiedni `div` z tekstem zgody w różnych językach i klika w rodzica `button`, co zapewnia skuteczniejszą interakcję z elementami strony.

## [1.14.0] - 2024-09-06
#### Nowe funkcjonalności:
- **Poprawa logiki klikania przycisku godzin otwarcia**: Ulepszono mechanizm znajdowania i klikania przycisku "open hours" w Google Maps. Teraz system lokalizuje element zawierający `jsaction="openhours"`, a następnie klika w jego element nadrzędny, co umożliwia poprawne otwarcie panelu z godzinami otwarcia.
- **Dodanie sprawdzania pełnego załadowania strony**: Wprowadzono mechanizm WebDriverWait, który upewnia się, że strona została w pełni załadowana przed wykonaniem jakichkolwiek operacji związanych z kliknięciem przycisku.

#### Poprawki błędów:
- **Poprawa obsługi elementu `jsaction`**: Naprawiono błąd związany z niewłaściwym wyszukiwaniem przycisku godzin otwarcia. Teraz `jsaction` jest wyszukiwany na podstawie zawartości, co rozwiązuje problem z nieodnalezieniem elementu na stronie.

#### Zmiany techniczne:po 
- **Lepsze logowanie elementów nadrzędnych**: Dodano logowanie elementu nadrzędnego przycisku "open hours" w konsoli, co ułatwia debugowanie i diagnozowanie problemów podczas operacji kliknięcia.

## [1.13.0] - 2024-09-06
#### Nowe funkcjonalności:
- **Poprawki zapisu cache**: Ulepszono logikę zapisu danych do pliku `cache.json`. Dodano sprawdzenie, czy dane są dostępne przed zapisem oraz dodatkowe logi, które informują, czy operacja zapisu zakończyła się sukcesem.
- **Lepsza obsługa zapytań bez wyników**: Zaimplementowano mechanizm, który w przypadku braku wyników wyszukiwania nie zapisuje pustych danych do cache, a jedynie loguje ostrzeżenie.
- **Korekta ścieżki do pliku cache**: Wprowadzono poprawki dotyczące ścieżki do pliku cache, co zapewnia poprawne tworzenie i zapisywanie danych w odpowiednim katalogu.
  
#### Poprawki błędów:
- **Naprawa pustego pliku cache**: Rozwiązano problem, w którym plik `cache.json` był tworzony, ale pozostawał pusty z powodu braku wyników wyszukiwania lub błędów w operacjach zapisu.

#### Zmiany techniczne:
- **Refaktoryzacja kodu klasy `Cache`**: Zoptymalizowano kod, w tym lepsze zarządzanie błędami podczas odczytu i zapisu pliku cache.

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