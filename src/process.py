import asyncio
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

        # Start live rendering
        with live:
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                location = row['Location']
                query = f"{restaurant_name} {location}"

                # Aktualizacja log_panel dla obecnej iteracji
                if verbose:
                    log_panel.title = f"ℹ️  Rozpoczęcie wyszukiwania dla: {query}"
                    layout['log'].update(log_panel)
                    live.update(layout)

                # Tworzenie asynchronicznego zadania
                task = Scraper.search_google(query, restaurant_name, table, log_panel, layout, live, verbose)
                tasks.append((task, index, restaurant_name))

                # Aktualizacja tabeli statusu
                table.add_row(restaurant_name, "[yellow]W trakcie[/yellow]")
                layout['table'].update(table)
                live.update(layout)

            # Oczekiwanie na zakończenie wszystkich zadań
            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            # Przetwarzanie wyników
            for result, index, restaurant_name in zip(results, [index for _, index, _ in tasks], [restaurant_name for _, _, restaurant_name in tasks]):
                if isinstance(result, Exception) or result == -1:
                    missing_count += 1
                    table.columns[1]._cells[index] = "[red]Brak danych[/red]"
                else:
                    found_count += 1
                    social_data = result.get('social_links', {})
                    for platform, platform_url in social_data.items():
                        df.at[index, platform] = platform_url
                    table.columns[1]._cells[index] = "[green]Zakończono[/green]"

                # Aktualizacja log_panel po zakończeniu operacji dla restauracji
                log_panel.title = f"{restaurant_name}: Zakończono operację"
                layout['log'].update(log_panel)
                live.update(layout)

        return df, found_count, missing_count

    @staticmethod
    async def process_hours(df, verbose, table, log_panel, layout, live):
        """Przetwarzanie godzin otwarcia z wyświetlaniem na żywo."""
        tasks = []
        found_count = 0
        missing_count = 0

        # Start live rendering for hours processing
        with live:
            for index, row in df.iterrows():
                restaurant_name = row['Name']
                google_url = row['Google']

                if google_url:
                    # Aktualizacja log_panel dla obecnej iteracji
                    if verbose:
                        log_panel.title = f"ℹ️ Rozpoczęcie pobierania godzin otwarcia dla: {restaurant_name}"
                        layout['log'].update(log_panel)
                        live.update(layout)

                    # Tworzenie asynchronicznego zadania
                    task = Scraper.get_opening_hours_from_google_maps(google_url, table, log_panel, layout, live, verbose)
                    tasks.append((task, index, restaurant_name))

                    # Aktualizacja tabeli statusu
                    table.add_row(restaurant_name, "[yellow]W trakcie[/yellow]")
                    layout['table'].update(table)
                    live.update(layout)

            # Oczekiwanie na zakończenie wszystkich zadań
            results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

            # Przetwarzanie wyników
            for result, index, restaurant_name in zip(results, [index for _, index, _ in tasks], [restaurant_name for _, _, restaurant_name in tasks]):
                if isinstance(result, Exception) or result is None:
                    missing_count += 1
                    table.columns[1]._cells[index] = "[red]Brak danych[/red]"
                else:
                    found_count += 1
                    df.at[index, 'Hours'] = result
                    table.columns[1]._cells[index] = "[green]Zakończono[/green]"

                # Aktualizacja log_panel po zakończeniu operacji dla restauracji
                log_panel.title = f"{restaurant_name}: Zakończono operację"
                layout['log'].update(log_panel)
                live.update(layout)

        return df, found_count, missing_count