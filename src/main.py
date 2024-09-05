import os
import click
import asyncio
import pandas as pd
from process import Process
from cache import Cache
from rich.console import Console

console = Console()

@click.command()
@click.option('--input_file', required=True, help='Ścieżka do pliku CSV z danymi.')
@click.option('--output_file', default='output.csv', help='Ścieżka do pliku, gdzie zapisane zostaną zaktualizowane dane.')
@click.option('--use_cache', is_flag=True, help='Czy używać cache do przyspieszenia wyszukiwań?')
@click.option('--verbose', is_flag=True, help='Wyświetlaj szczegółowe informacje o przebiegu.')
@click.option('--social', is_flag=True, help='Uzupełniaj brakujące profile społecznościowe.')
@click.option('--hours', is_flag=True, help="Pobierz godziny otwarcia z Google Maps.")
def main(input_file, output_file, use_cache, verbose, social, hours):
    """
    Skrypt uzupełnia brakujące dane w pliku CSV poprzez wyszukiwanie informacji na Google.
    Plik CSV należy zapodać przez --input_file, a wynik zostanie zapisany w --output_file.
    """
    
    if not social and not hours:
        console.print("[bold red]❌ Nie wybrano funkcji. Użyj --help, aby zobaczyć dostępne opcje.[/bold red]")
        click.echo(main.get_help(click.Context(main)))
        return

    try:
        df = pd.read_csv(input_file)
        console.print(f"[bold green]✅ Wczytano plik {input_file}.[/bold green]")
    except FileNotFoundError:
        console.print(f"[bold red]❌ Plik {input_file} nie został znaleziony.[/bold red]")
        return

    cache = Cache() if use_cache else None

    # Przetwarzanie danych społecznościowych
    if social:
        df, found_count, missing_count = asyncio.run(Process.process_social_data(df, cache, verbose))
        console.print(f"[bold green]✅ Przetworzono {found_count} znalezionych rekordów i {missing_count} brakujących.[/bold green]")

    # Przetwarzanie godzin otwarcia
    if hours:
        df = asyncio.run(Process.process_hours(df, verbose))

    # Zapisanie zaktualizowanego pliku CSV
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as exc:
            console.print(f"[bold red]❌ Błąd podczas tworzenia katalogu: {exc}[/bold red]")
            return
    
    df.to_csv(output_file, index=False)
    console.print(f"[bold green]✅ Zapisano zaktualizowany plik CSV w {output_file}.[/bold green]")

    if cache:
        cache.save_cache()

if __name__ == "__main__":
    main()