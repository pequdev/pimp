import asyncio
import pandas as pd
from rich.console import Console
from rich.table import Table
from urllib.parse import urlparse, urlunparse
from scraper import Scraper

console = Console()

class Process:
    @staticmethod
    def clean_url(url):
        """Czyszczenie URL-a z niepotrzebnych parametrów."""
        parsed_url = urlparse(url)
        return urlunparse(parsed_url._replace(query=''))

    @staticmethod
    def build_query(bar_name, location):
        """Budowanie zapytania na podstawie nazwy baru i lokalizacji."""
        return f"{bar_name} {location}"

    @staticmethod
    async def process_social_data(df, cache, verbose):
        """Przetwarzanie danych społecznościowych z obsługą cache."""
        # Dodajemy kolumnę 'SocialData', jeśli jeszcze nie istnieje
        if 'SocialData' not in df.columns:
            df['SocialData'] = None

        tasks = []
        found_count = 0
        missing_count = 0

        table = Table(title="Status wyszukiwania danych społecznościowych")
        table.add_column("Nazwa", justify="left")
        table.add_column("Platforma", justify="left")
        table.add_column("Status", justify="right")

        for index, row in df.iterrows():
            restaurant_name = row['Name']
            location = row['Location']
            query = Process.build_query(restaurant_name, location)

            # Sprawdzenie cache przed wyszukiwaniem
            cached_result = cache.get(query) if cache else None
            if cached_result:
                if verbose:
                    Scraper.report(f"Wynik dla '{restaurant_name}' pobrany z cache.", "success")
                df.at[index, 'SocialData'] = cached_result
                found_count += 1
            else:
                if verbose:
                    Scraper.report(f"Rozpoczęcie wyszukiwania dla: {restaurant_name} ({location})", "info")
                task = Scraper.search_google(query, verbose)
                tasks.append((task, index, restaurant_name))

        # Uruchomienie zadań asynchronicznych dla danych, których nie było w cache
        results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

        # Przetwarzanie wyników
        for result, index, restaurant_name in zip(results, [index for _, index, _ in tasks], [restaurant_name for _, _, restaurant_name in tasks]):
            if isinstance(result, Exception):
                missing_count += 1
                table.add_row(restaurant_name, "Wszystkie platformy", "[red]Błąd[/red]")
                if verbose:
                    Scraper.report(f"Błąd podczas wyszukiwania dla '{restaurant_name}': {result}", "error")
            else:
                found_count += 1
                df.at[index, 'SocialData'] = result
                if cache:
                    cache.set(query, result)  # Zapis do cache
                table.add_row(restaurant_name, "Wszystkie platformy", "[green]Znaleziono[/green]")

        if verbose:
            console.print(table)

        return df, found_count, missing_count

    @staticmethod
    async def process_hours(df, verbose):
        """Przetwarzanie godzin otwarcia dla lokali z obsługą cache."""
        tasks = []

        table = Table(title="Status pobierania godzin otwarcia")
        table.add_column("Nazwa", justify="left")
        table.add_column("Status", justify="right")

        for index, row in df.iterrows():
            google_url = row['Google']
            restaurant_name = row['Name']

            if google_url:
                Scraper.report(f"Rozpoczęcie pobierania godzin otwarcia dla: {restaurant_name}", "info")
                # Tworzenie zadania dla Scraper.get_opening_hours
                task = asyncio.create_task(Process.get_and_update_hours(df, index, google_url, restaurant_name, verbose))
                tasks.append(task)

        # Uruchomienie zadań asynchronicznych
        await asyncio.gather(*tasks)

        if verbose:
            console.print(table)

        return df

    @staticmethod
    async def get_and_update_hours(df, index, google_url, restaurant_name, verbose):
        """Pobieranie i aktualizacja godzin otwarcia dla danego lokalu."""
        try:
            hours = await Scraper.get_opening_hours(google_url, verbose)
            df.at[index, 'Hours'] = hours
            if verbose:
                Scraper.report(f"Zakończono pobieranie godzin otwarcia dla: {restaurant_name}", "success")
        except Exception as e:
            if verbose:
                Scraper.report(f"Błąd przy pobieraniu godzin otwarcia dla {restaurant_name}: {e}", "error")