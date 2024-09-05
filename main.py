import click
import asyncio
import pandas as pd
from scraper import search_google
from cache import Cache
from rich.console import Console
from rich.progress import Progress, track
from rich.live import Live
from rich.table import Table
import time

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

def build_query(bar_name, platform):
    return f"{bar_name} {platform}"

async def process_missing_data(df, cache, verbose):
    tasks = []
    found_count = 0
    missing_count = 0
    total_tasks = len(df) * len(DOMAIN_MAP)

    progress = Progress()
    task_id = progress.add_task("[green]Przetwarzanie danych...", total=total_tasks)

    table = Table(title="Status zadań asyncio")
    table.add_column("Nazwa", justify="left")
    table.add_column("Platforma", justify="left")
    table.add_column("Status", justify="right")

    live_table = Live(table, console=console, refresh_per_second=2)

    async with live_table:
        for index, row in df.iterrows():
            for platform in DOMAIN_MAP.keys():
                if row[platform] == 0:
                    query = build_query(row['Name'], platform)
                    domain = DOMAIN_MAP[platform]
                    if verbose:
                        console.log(f"🚀 Wyszukiwanie: {query}")
                    task = search_google(query, domain)
                    tasks.append((task, index, platform, row['Name']))

        results = await asyncio.gather(*[task for task, _, _, _ in tasks], return_exceptions=True)

        for i, (result, index, platform, bar_name) in enumerate(zip(results, [index for _, index, _, _ in tasks], 
                                                                    [platform for _, _, platform, _ in tasks], 
                                                                    [bar_name for _, _, _, bar_name in tasks])):
            if isinstance(result, Exception):
                missing_count += 1
                table.add_row(bar_name, platform, "[red]Błąd[/red]")
                if verbose:
                    console.log(f"[bold red]❌ Błąd: {result}[/bold red]")
            else:
                found_count += 1
                df.at[index, platform] = result
                table.add_row(bar_name, platform, "[green]Zakończono[/green]")

            progress.update(task_id, advance=1)
            time.sleep(0.1)

    return df, found_count, missing_count

@click.command()
@click.option('--input_file', required=True, help='Ścieżka do pliku CSV z danymi.')
@click.option('--output_file', default='output.csv', help='Ścieżka do pliku, gdzie zapisane zostaną zaktualizowane dane.')
@click.option('--use_cache', is_flag=True, help='Czy używać cache do przyspieszenia wyszukiwań?')
@click.option('--verbose', is_flag=True, help='Wyświetlaj szczegółowe informacje o przebiegu.')
@click.option('--social', is_flag=True, help='Uzupełniaj brakujące profile społecznościowe.')
def main(input_file, output_file, use_cache, verbose, social):
    if not social:
        console.print("[bold red]❌ Nie wybrano funkcji. Użyj --help, aby zobaczyć dostępne opcje.[/bold red]")
        click.echo(main.get_help(click.Context(main)))
        return

    try:
        df = pd.read_csv(input_file)
        console.print(f"[bold green]✅ Wczytano plik {input_file}.[/bold green]")
    except FileNotFoundError:
        console.print(f"[bold red]❌ Plik {input_file} nie został znaleziony.[/bold red]")
        return

    if verbose:
        console.print(f"[bold green]ℹ️ Używanie cache: {use_cache}[/bold green]" if use_cache else "[bold yellow]⚠️ Cache nie używany[/bold yellow]")

    cache = Cache() if use_cache else None

    updated_df, found_count, missing_count = asyncio.run(process_missing_data(df, cache, verbose))

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