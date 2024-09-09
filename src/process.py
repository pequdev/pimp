import asyncio
from concurrent.futures import ProcessPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from src.scraper import Scraper

console = Console()

class Process:
    @staticmethod
    async def process_social_data(df, cache, verbose, table, log_panel, layout, live):
        """Przetwarzanie danych społecznościowych z wyświetlaniem na żywo."""
        tasks = []
        found_count = 0
        missing_count = 0

        with ProcessPoolExecutor() as pool:
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                location = row['Location']
                query = f"{restaurant_name} {location}"

                if verbose:
                    log_panel.title = f"ℹ️  Rozpoczęcie wyszukiwania dla: {query}"
                    layout['log'].update(log_panel)
                    live.update(layout)

                # Uruchomienie Scraper w osobnym procesie
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(pool, Process._run_search_google_in_process, query, restaurant_name, verbose)
                tasks.append((task, index, restaurant_name))

            # Oczekiwanie na zakończenie wszystkich zadań
            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            updated_rows = []
            for result, (task, index, restaurant_name) in zip(results, tasks):
                if isinstance(result, Exception) or result == -1:
                    missing_count += 1
                    status = "[red]Brak danych[/red]"
                else:
                    found_count += 1
                    social_data = result.get('social_links', {})
                    for platform, platform_url in social_data.items():
                        df.at[index, platform] = platform_url
                    status = "[green]Zakończono[/green]"

                updated_rows.append((restaurant_name, status))

            # Aktualizacja interfejsu po zakończeniu przetwarzania (w głównym procesie)
            new_table = Table(title="Status przetwarzania")
            new_table.add_column("Nazwa")
            new_table.add_column("Status")

            for row in updated_rows:
                new_table.add_row(*row)

            layout['table'].update(new_table)
            live.update(layout)

        return df, found_count, missing_count

    @staticmethod
    async def process_hours(df, verbose, table, log_panel, layout, live):
        """Przetwarzanie godzin otwarcia z wyświetlaniem na żywo."""
        tasks = []
        found_count = 0
        missing_count = 0

        with ProcessPoolExecutor() as pool:
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                google_url = row['Google']

                if google_url:
                    if verbose:
                        log_panel.title = f"ℹ️ Rozpoczęcie pobierania godzin otwarcia dla: {restaurant_name}"
                        layout['log'].update(log_panel)
                        live.update(layout)

                    # Uruchomienie Scraper w osobnym procesie
                    loop = asyncio.get_event_loop()
                    # Przekazujemy tylko wymagane argumenty
                    task = loop.run_in_executor(
                        pool, Process._run_get_opening_hours_in_process, google_url, restaurant_name, verbose
                    )
                    tasks.append((task, index, restaurant_name))

                    table.add_row(restaurant_name, "[yellow]W trakcie[/yellow]")
                    layout['table'].update(table)
                    live.update(layout)

            # Oczekiwanie na zakończenie wszystkich zadań
            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            updated_rows = []
            for result, (task, index, restaurant_name) in zip(results, tasks):
                if isinstance(result, Exception) or result is None:
                    missing_count += 1
                    status = "[red]Brak danych[/red]"
                else:
                    found_count += 1
                    df.at[index, 'Hours'] = result
                    status = "[green]Zakończono[/green]"

                updated_rows.append((restaurant_name, status))

                log_panel.title = f"{restaurant_name}: Zakończono operację"
                layout['log'].update(log_panel)
                live.update(layout)

            # Aktualizacja tabeli po zakończeniu przetwarzania
            new_table = Table(title="Status przetwarzania")
            new_table.add_column("Nazwa")
            new_table.add_column("Status")

            for row in updated_rows:
                new_table.add_row(*row)

            layout['table'].update(new_table)
            live.update(layout)

        return df, found_count, missing_count

    @staticmethod
    def _run_search_google_in_process(query, restaurant_name, verbose):
        """Funkcja uruchamiana w osobnym procesie do wyszukiwania danych społecznościowych."""
        # Tworzenie WebDrivera lokalnie w procesie
        driver = Scraper.initialize_webdriver()
        result = Scraper.search_google(query, restaurant_name, verbose)
        Scraper.close_webdriver(driver)
        return result

    @staticmethod
    def _run_get_opening_hours_in_process(google_url, restaurant_name, verbose):
        """Funkcja uruchamiana w osobnym procesie do pobierania godzin otwarcia."""
        # Tworzenie WebDrivera lokalnie w procesie
        driver = Scraper.initialize_webdriver()
        result = Scraper.get_opening_hours_from_google_maps(google_url, verbose)
        Scraper.close_webdriver(driver)
        return result