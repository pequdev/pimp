import os
import click
import asyncio
import pandas as pd
from scraper import search_google
from cache import Cache
from rich.console import Console
from rich.progress import Progress, track
from rich.live import Live
from rich.table import Table
from rich.progress import BarColumn, TimeElapsedColumn, SpinnerColumn
from urllib.parse import urlparse, urlunparse

console = Console()

# Mapowanie platform społecznościowych na domeny
DOMAIN_MAP = {
    'Instagram': 'instagram.com',
    'TikTok': 'tiktok.com',
    'Facebook': 'facebook.com',
    'YouTube': 'youtube.com',
    'UberEats': 'ubereats.com',
    'TripAdvisor': 'tripadvisor.com',
    'TheFork': 'thefork.com'
}

# Budowanie zapytania na podstawie nazwy baru i lokalizacji
def build_query(bar_name, location):
    return f"{bar_name} {location}"

# Funkcja czyszcząca URL z niepotrzebnych parametrów
def clean_url(url):
    parsed_url = urlparse(url)
    clean_url = urlunparse(parsed_url._replace(query=''))  # Usuwamy parametry z URL-a
    return clean_url

# Dynamiczne monitorowanie zadań asyncio
async def process_missing_data(df, cache, verbose):
    tasks = []
    found_count = 0
    missing_count = 0

    # Przygotowanie progresu i tabeli do wyświetlania w konsoli
    progress = Progress(
        SpinnerColumn(),  
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeElapsedColumn()
    )
    task_id = progress.add_task("[green]Przetwarzanie danych...", total=len(df))

    # Tabela dla wyników wyszukiwania
    table = Table(title="Status zadań async")
    table.add_column("Nazwa", justify="left")
    table.add_column("Platforma", justify="left")
    table.add_column("Status", justify="right")

    live_table = Live(table, console=console, refresh_per_second=4)

    # Konwertujemy kolumny na typ str, aby uniknąć ostrzeżeń o niezgodnych typach
    for platform in DOMAIN_MAP.keys():
        if platform in df.columns:
            df[platform] = df[platform].astype(str)

    with progress, live_table:
        for index, row in df.iterrows():
            # Budowanie zapytania na podstawie nazwy i lokalizacji
            restaurant_name = row['Name']
            location = row['Location']
            query = build_query(restaurant_name, location)

            if verbose:
                console.log(f"🚀 Rozpoczęcie wyszukiwania dla: {query}")
            
            task = search_google(query, verbose)
            tasks.append((task, index, restaurant_name))

        results = await asyncio.gather(*[task for task, _, _ in tasks], return_exceptions=True)

        for i, (result, index, restaurant_name) in enumerate(zip(results, [index for _, index, _ in tasks], 
                                                                 [restaurant_name for _, _, restaurant_name in tasks])):
            if isinstance(result, Exception):
                missing_count += 1
                table.add_row(restaurant_name, "Wszystkie platformy", "[red]Błąd[/red]")
                if verbose:
                    console.log(f"[bold red]❌ Wystąpił błąd podczas wyszukiwania dla '{restaurant_name}': {result}[/bold red]")
            else:
                found_count += 1

                # Wyświetlanie wyniku w zwięzły sposób
                if verbose:
                    console.log(f"🔍 Wynik wyszukiwania dla '{restaurant_name}' zakończony pomyślnie.")

                # Czyszczenie URL-i z niepotrzebnych parametrów i aktualizacja tabeli
                for platform in DOMAIN_MAP.keys():
                    platform_key = platform.lower()
                    if result.get(platform_key):
                        clean_link = clean_url(result[platform_key])  # Usunięcie zbędnych parametrów
                        df.at[index, platform] = clean_link
                        table.add_row(restaurant_name, platform, "[green]Zakończono[/green]")

            progress.update(task_id, advance=1)
            await asyncio.sleep(0.1)

    return df, found_count, missing_count

# Dodajemy CLI przy pomocy Click
@click.command()
@click.option('--input_file', required=True, help='Ścieżka do pliku CSV z danymi.')
@click.option('--output_file', default='output.csv', help='Ścieżka do pliku, gdzie zapisane zostaną zaktualizowane dane.')
@click.option('--use_cache', is_flag=True, help='Czy używać cache do przyspieszenia wyszukiwań?')
@click.option('--verbose', is_flag=True, help='Wyświetlaj szczegółowe informacje o przebiegu.')
@click.option('--social', is_flag=True, help='Uzupełniaj brakujące profile społecznościowe.')
def main(input_file, output_file, use_cache, verbose, social):
    """
    Skrypt uzupełnia brakujące dane w pliku CSV poprzez wyszukiwanie informacji na Google.
    Plik CSV należy zapodać przez --input_file, a wynik zostanie zapisany w --output_file.
    """
    
    # Sprawdzamy, czy podano flagę --social
    if not social:
        console.print("[bold red]❌ Nie wybrano funkcji. Użyj --help, aby zobaczyć dostępne opcje.[/bold red]")
        # Wyświetlenie standardowego helpa
        click.echo(main.get_help(click.Context(main)))
        return

    # Ładowanie pliku CSV
    try:
        df = pd.read_csv(input_file)
        console.print(f"[bold green]✅ Wczytano plik {input_file}.[/bold green]")
    except FileNotFoundError:
        console.print(f"[bold red]❌ Plik {input_file} nie został znaleziony.[/bold red]")
        return

    if verbose:
        console.print(f"[bold green]ℹ️ Używanie cache: {use_cache}[/bold green]" if use_cache else "[bold yellow]⚠️ Cache nie używany[/bold yellow]")

    # Ładowanie cache
    cache = Cache() if use_cache else None

    # Przetwarzanie brakujących danych
    updated_df, found_count, missing_count = asyncio.run(process_missing_data(df, cache, verbose))

    # Zapisanie zaktualizowanego pliku CSV
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)  # Używamy exist_ok=True, aby zapobiec błędom
        except OSError as exc:
            console.print(f"[bold red]❌ Błąd podczas tworzenia katalogu: {exc}[/bold red]")
            return
    
    updated_df.to_csv(output_file, index=False)
    console.print(f"[bold green]✅ Zapisano zaktualizowany plik CSV w {output_file}.[/bold green]")

    if cache:
        cache.save_cache()

    if verbose:
        console.print(f"[bold green]✅ Przetworzono {found_count} znalezionych rekordów i {missing_count} brakujących.[/bold green]")
    else:
        console.print(f"[bold blue]ℹ️ Przetworzono rekordy: {found_count} znalezionych, {missing_count} brakujących.[/bold blue]")

if __name__ == "__main__":
    main()