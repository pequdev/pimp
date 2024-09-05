# PIMP - Profiling Information Management Platform

**PIMP** to aplikacja web scrapingowa, która asynchronicznie przeszukuje Google i inne takie.

# Analiza danych konkurencji dla lokali gastronomicznych

Ten projekt służy do automatycznej analizy danych konkurencji dla lokali gastronomicznych, w tym wyszukiwania profili społecznościowych oraz stron internetowych restauracji na podstawie danych z Google.

## Funkcjonalności

- **Automatyczne wyszukiwanie danych społecznościowych**: Skrypt przeszukuje Google w poszukiwaniu profili na platformach społecznościowych takich jak Instagram, TikTok, Facebook, YouTube, oraz serwisów recenzji jak TripAdvisor czy TheFork.
- **Pobieranie godzin otwarcia**: Narzędzie pozwala na automatyczne pobieranie godzin otwarcia restauracji z Google Maps.
- **Obsługa cache**: Wyniki wyszukiwania mogą być przechowywane w pliku cache, co przyspiesza kolejne wyszukiwania.
- **Dynamiczne raportowanie**: Proces przetwarzania danych jest dynamicznie raportowany w terminalu przy użyciu biblioteki `rich.console` oraz `rich.live`.

## Wymagania

- **Python**: 3.8 lub nowszy
- **Pip**: do instalacji zależności
- **Google Chrome**: do automatyzacji wyszukiwania
- **ChromeDriver**: do kontrolowania przeglądarki Chrome przez Selenium

## Instalacja

1. **Sklonuj repozytorium:**

   ```bash
   git clone https://github.com/pequx/pimp.git
   cd pimp
   ```

2. **Tworzenie środowiska wirtualnego i instalacja zależności:**

   Użyj `Makefile`, aby automatycznie utworzyć środowisko wirtualne i zainstalować zależności:

   ```bash
   make install
   ```

   Możesz również zaktualizować zależności po zmianie pliku `requirements.txt`:

   ```bash
   make update_venv
   ```

3. **Instalacja ChromeDriver:**

   Skrypt korzysta z ChromeDriver, który można zainstalować za pomocą Homebrew:

   ```bash
   make chromedriver
   ```

4. **Wejście do środowiska wirtualnego:**

   Aby wejść do wirtualnego środowiska, użyj poniższej komendy:

   ```bash
   source venv/bin/activate
   ```

## Użycie

Skrypt przyjmuje plik CSV jako wejście, przeszukuje dane w Google, pobiera brakujące profile społecznościowe, strony internetowe oraz godziny otwarcia, a następnie zapisuje wyniki w nowym pliku CSV.

### Przykład:

```bash
python3 main.py --input_file data/input.csv --output_file data/output.csv --social --hours --use_cache --verbose
```

### Opcje:

- `--input_file`: Ścieżka do pliku CSV z danymi wejściowymi (wymagane)
- `--output_file`: Ścieżka do pliku, gdzie zapisane zostaną zaktualizowane dane (domyślnie: `output.csv`)
- `--social`: Włącza uzupełnianie profili społecznościowych
- `--hours`: Pobiera godziny otwarcia z Google Maps
- `--use_cache`: Używa pliku cache do przyspieszenia wyszukiwań
- `--verbose`: Wyświetla szczegółowe informacje o przebiegu

## Struktura projektu

- `src/`: Zawiera główny kod projektu
- `tests/`: Testy jednostkowe projektu
- `data/`: Zawiera dane wejściowe i wyjściowe w formacie CSV
- `venv/`: Środowisko wirtualne z zainstalowanymi zależnościami
- `Makefile`: Zawiera komendy do automatyzacji instalacji i konfiguracji
- `requirements.txt`: Lista wymaganych bibliotek Pythona

## Autor

Projekt stworzony przez pequ.dev.

## Licencja

Ten projekt jest licencjonowany na licencji MIT.