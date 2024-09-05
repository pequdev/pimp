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
        parsed_url = urlparse(url)
        clean_url = urlunparse(parsed_url._replace(query=''))  # Usuwamy parametry z URL-a
        return clean_url

    @staticmethod
    def build_query(bar_name, location):
        return f"{bar_name} {location}"

    @staticmethod
    async def process_social_data(df, cache, verbose):
        tasks = []
        found_count = 0
        missing_count = 0

        table = Table(title="Status zadań async")
        table.add_column("Nazwa", justify="left")
        table.add_column("Platforma", justify="left")
        table.add_column("Status", justify="right")

        live_table = Live(table, console=console, refresh_per_second=4)

        for platform in DOMAIN_MAP.keys():
            if platform in df.columns:
                df[platform] = df[platform].astype(str)

        with live_table:
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                location = row['Location']
                query = Process.build_query(restaurant_name, location)

                if verbose:
                    tree = Tree(f"🚀 Rozpoczęcie wyszukiwania dla: {query}")
                
                task = Scraper.search_google(query, verbose)
                tasks.append((task, index, restaurant_name))

            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            for i, (result, index, restaurant_name) in enumerate(zip(results, [index for _, index, _ in tasks], 
                                                                     [restaurant_name for _, _, restaurant_name in tasks])):
                if isinstance(result, Exception) or result == -1 or result is None:
                    missing_count += 1
                    table.add_row(restaurant_name, "Wszystkie platformy", "[red]Brak danych[/red]")
                    if verbose:
                        tree.add(f"[red]❌ Brak wyników wyszukiwania dla '{restaurant_name}'")
                else:
                    found_count += 1

                    if verbose:
                        tree.add(f"🔍 Wynik wyszukiwania dla '{restaurant_name}' zakończony pomyślnie.")

                    # Przetwarzanie zwróconych linków społecznościowych i strony domowej
                    social_data = result.get('social_links', {})
                    website_link = result.get('website', "")

                    for platform in DOMAIN_MAP.keys():
                        platform_key = platform.lower()
                        if social_data.get(platform_key):
                            clean_link = Process.clean_url(social_data[platform_key])  # Usunięcie zbędnych parametrów
                            df.at[index, platform] = clean_link
                            table.add_row(restaurant_name, platform, "[green]Zakończono[/green]")
                        else:
                            df.at[index, platform] = ""

                    # Przypisanie linków do odpowiednich kolumn
                    tripadvisor_link = social_data.get('tripadvisor', "")
                    thefork_link = social_data.get('thefork', "")

                    if tripadvisor_link:
                        df.at[index, 'TripAdvisor'] = Process.clean_url(tripadvisor_link)
                    else:
                        df.at[index, 'TripAdvisor'] = ""

                    if thefork_link:
                        df.at[index, 'TheFork'] = Process.clean_url(thefork_link)
                    else:
                        df.at[index, 'TheFork'] = ""

                    # Aktualizacja kolumny 'Website' - wykluczenie stron z TripAdvisor, TheFork, Yelp, itp.
                    if website_link and not any(platform in website_link for platform in ['tripadvisor.com', 'thefork.com', 'yelp.com']):
                        clean_website_link = Process.clean_url(website_link)
                        df.at[index, 'Website'] = clean_website_link
                        table.add_row(restaurant_name, "Strona domowa", "[green]Zakończono[/green]")
                    else:
                        df.at[index, 'Website'] = ""

            if verbose:
                console.print(Panel(tree, title="Wynik wyszukiwania", expand=False))

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