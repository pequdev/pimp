import json
import pandas as pd
import asyncio
from scraper import Scraper
from urllib.parse import urlparse, urlunparse
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.tree import Tree
from rich.panel import Panel

console = Console()

DOMAIN_MAP = {
    'Instagram': 'instagram.com',
    'TikTok': 'tiktok.com',
    'Facebook': 'facebook.com',
    'YouTube': 'youtube.com',
    'UberEats': 'ubereats.com',
    'TripAdvisor': 'tripadvisor.com',
    'TheFork': 'thefork.com'
}

class Process:
    @staticmethod
    def clean_url(url):
        """Czyści URL z parametrów zapytania."""
        parsed_url = urlparse(url)
        clean_url = urlunparse(parsed_url._replace(query=''))
        return clean_url

    @staticmethod
    def build_query(bar_name, location):
        """Buduje zapytanie do wyszukiwania w Google na podstawie nazwy lokalu i lokalizacji."""
        return f"{bar_name} {location}"

    @staticmethod
    def enforce_dtypes(df):
        """Wymusza odpowiednie typy danych w kolumnach."""
        columns_to_convert = ['Website', 'Google', 'UberEats', 'Instagram', 'TikTok', 'Facebook', 'YouTube', 'TripAdvisor', 'TheFork']
        df[columns_to_convert] = df[columns_to_convert].astype('object')
        return df

    @staticmethod
    def is_potential_website_based_on_name(website_link, restaurant_name):
        """
        Funkcja, która ocenia, czy domena strony zawiera nazwę restauracji lub jej fragmenty.
        Sprawdza, czy fragment nazwy restauracji jest częścią domeny.
        """
        parsed_website = urlparse(website_link).netloc.lower()
        restaurant_name_words = restaurant_name.lower().split()

        # Jeśli więcej niż jedno słowo pasuje do domeny, uznajemy stronę za prawdopodobną stronę domową
        matching_words = [word for word in restaurant_name_words if word in parsed_website]
        return len(matching_words) > 0

    @staticmethod
    async def process_social_data(df, cache, verbose):
        tasks = []
        found_count = 0
        missing_count = 0

        table = Table(title="Status wyszukiwania danych społecznościowych i stron domowych")
        table.add_column("Nazwa", justify="left", style="cyan", no_wrap=True)
        table.add_column("Platforma", justify="left", style="magenta")
        table.add_column("Status", justify="center", style="green")

        with Live(table, console=console, refresh_per_second=4):
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                location = row['Location']
                query = f"{restaurant_name} {location}"

                if verbose:
                    console.print(f"ℹ️  Rozpoczęcie wyszukiwania dla: {query}")
                
                task = Scraper.search_google(query, restaurant_name, verbose)
                tasks.append((task, index, restaurant_name))

            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            for result, index, restaurant_name in zip(results, [index for _, index, _ in tasks], 
                                                    [restaurant_name for _, _, restaurant_name in tasks]):
                if isinstance(result, Exception) or result == -1 or result is None:
                    missing_count += 1
                    table.add_row(restaurant_name, "Wszystkie platformy", "[red]Brak danych[/red]")
                else:
                    found_count += 1
                    social_data = result.get('social_links', {})
                    website_link = result.get('website', "")

                    # Przetwarzanie linków społecznościowych
                    for platform, platform_url in social_data.items():
                        df.at[index, platform] = platform_url if platform_url else ""
                        table.add_row(restaurant_name, platform, "[green]Zakończono[/green]")

                    # Sprawdzanie linków domowych (jeśli są)
                    if website_link:
                        df.at[index, 'Website'] = website_link
                        table.add_row(restaurant_name, "Strona domowa", "[green]Zakończono[/green]")
                    else:
                        df.at[index, 'Website'] = ""

        return df, found_count, missing_count

    @staticmethod
    async def process_hours(df, verbose):
        tasks = []
        found_count = 0
        missing_count = 0

        table = Table(title="Status zadań async")
        table.add_column("Nazwa", justify="left")
        table.add_column("Status", justify="right")

        live_table = Live(table, console=console, refresh_per_second=4)

        with live_table:
            for index, row in df.iterrows():
                google_url = row['Google']
                restaurant_name = row['Name']

                if google_url:
                    if verbose:
                        tree = Tree(f"🚀 Rozpoczęcie pobierania godzin otwarcia dla: {restaurant_name}")
                    
                    task = asyncio.create_task(Process.get_and_update_hours(df, index, google_url, restaurant_name, verbose, tree))
                    tasks.append(task)

            # Równoczesne uruchomienie wszystkich zadań
            await asyncio.gather(*tasks)

        df = Process.enforce_dtypes(df)
        return df
    
    @staticmethod
    async def get_and_update_hours(df, index, google_url, restaurant_name, verbose, tree):
        try:
            hours = await Scraper.get_opening_hours(google_url)
            df.at[index, 'Hours'] = hours

            if verbose:
                tree.add(f"[green]✅ Zakończono pobieranie godzin otwarcia dla: {restaurant_name}[/green]")
        except Exception as e:
            if verbose:
                tree.add(f"[red]❌ Błąd przy pobieraniu godzin otwarcia dla {restaurant_name}: {e}[/red]")

        if verbose:
            console.print(Panel(tree, title=f"Wynik pobierania godzin otwarcia dla: {restaurant_name}", expand=False))