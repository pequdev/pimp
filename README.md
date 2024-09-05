# PIMP - Profiling Information Management Platform

**PIMP** to aplikacja web scrapingowa, która asynchronicznie przeszukuje Google w celu uzupełnienia brakujących profili społecznościowych dla podanych firm. Wykorzystuje Selenium do automatyzacji wyszukiwań oraz `asyncio` do zarządzania asynchronicznymi zadaniami.

## Funkcjonalności
- Asynchroniczne wyszukiwanie profili społecznościowych i platform (np. Instagram, TikTok, Facebook, YouTube, UberEats, TripAdvisor, TheFork).
- Dynamiczne monitorowanie zadań asynchronicznych w terminalu z użyciem progres bara i statusów zadań (zakończono/błąd).
- Obsługa cache, aby uniknąć ponownych zapytań Google.
- Możliwość użycia opcji CLI do personalizacji działania aplikacji (np. `--social`, `--verbose`).

## Wymagania
- Python 3.x
- Google Chrome
- ChromeDriver (dopasowany do wersji przeglądarki)

## Instalacja

### 1. Sklonowanie repozytorium

Sklonuj repozytorium i przejdź do katalogu projektu:

```bash
git clone <repo_url>
cd project_root