import os
import click
import asyncio
import pandas as pd
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from src.process import Process
from src.cache import Cache
from rich.console import Console

console = Console()

# Klasa do obsługi Google Sheets
class GoogleSheetsManager:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, verbose=False):
        # Ścieżka do pliku z poświadczeniami JSON
        self.verbose = verbose
        credentials_file = os.path.join('data', 'pequ-dev-578d98c90f74.json')
        self.creds = self.authorize_google_sheets(credentials_file)
        if self.verbose:
            console.print(f"[bold green]🔑 Autoryzacja za pomocą pliku: {credentials_file}[/bold green]")
        self.client = gspread.authorize(self.creds)

    def authorize_google_sheets(self, credentials_file):
        """Autoryzacja Google Sheets API przy użyciu konta serwisowego."""
        if self.verbose:
            console.print("[yellow]🔄 Rozpoczynam autoryzację Google Sheets...[/yellow]")
        
        creds = Credentials.from_service_account_file(credentials_file, scopes=self.SCOPES)
        
        if self.verbose:
            console.print(f"[bold green]✅ Pomyślnie autoryzowano za pomocą pliku {credentials_file}[/bold green]")
        
        return creds

    def get_google_sheet_as_df(self, sheet_id, sheet_name, sheet_range):
        """Pobiera dane z Google Sheets jako DataFrame."""
        if self.verbose:
            console.print(f"[yellow]🔄 Pobieranie danych z arkusza Google Sheets o ID: {sheet_id} i nazwie: {sheet_name}[/yellow]")
        
        console.log(self.client)
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        
        if self.verbose:
            console.print(f"[bold green]✅ Pobrano dane z zakresu {sheet_range} arkusza {sheet_name} (ID: {sheet_id})[/bold green]")
        
        return pd.DataFrame(data)

    def update_google_sheet_from_df(self, sheet_id, sheet_name, sheet_range, df):
        """Aktualizuje Google Sheets danymi z DataFrame."""
        if self.verbose:
            console.print(f"[yellow]🔄 Aktualizacja arkusza Google Sheets o ID: {sheet_id} i nazwie: {sheet_name}[/yellow]")
        
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        data = df.values.tolist()
        sheet.update(sheet_range, data)
        
        if self.verbose:
            console.print(f"[bold green]✅ Pomyślnie zaktualizowano dane w arkuszu {sheet_name} (ID: {sheet_id}) w zakresie {sheet_range}[/bold green]")

class CommandManager:
    def __init__(self, df, cache, verbose):
        self.df = df
        self.cache = cache
        self.verbose = verbose

    async def process_social_data(self):
        """Przetwarzanie danych społecznościowych."""
        try:
            self.df, found_count, missing_count = await Process.process_social_data(self.df, self.cache, self.verbose)
            console.print(f"[bold green]✅ Przetworzono {found_count} znalezionych rekordów i {missing_count} brakujących.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Błąd przy przetwarzaniu danych społecznościowych: {e}[/bold red]")
            raise

    async def process_hours(self):
        """Przetwarzanie godzin otwarcia."""
        try:
            self.df, found_count, missing_count = await Process.process_hours(self.df, self.verbose)
            console.print(f"[bold green]✅ Przetworzono {found_count} znalezionych rekordów i {missing_count} brakujących.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Błąd przy przetwarzaniu godzin otwarcia: {e}[/bold red]")
            raise

def initialize_cache(use_cache):
    """Inicjalizacja cache."""
    if use_cache:
        return Cache()
    return None

@click.command()
@click.option('--sheet_id', required=True, help='ID arkusza Google Sheets z danymi.')
@click.option('--sheet_name', required=True, help='Nazwa arkusza Google Sheets do użycia.')
@click.option('--sheet_range', default='A1:Z1000', help='Zakres danych w arkuszu Google Sheets.')
@click.option('--use_cache', is_flag=True, help='Czy używać cache do przyspieszenia wyszukiwań?')
@click.option('--verbose', is_flag=True, help='Wyświetlaj szczegółowe informacje o przebiegu.')
@click.option('--social', is_flag=True, help='Uzupełniaj brakujące profile społecznościowe.')
@click.option('--hours', is_flag=True, help="Pobierz godziny otwarcia z Google Maps.")
def main(sheet_id, sheet_name, sheet_range, use_cache, verbose, social, hours):
    """
    Skrypt uzupełnia brakujące dane w arkuszu Google Sheets poprzez wyszukiwanie informacji na Google.
    Arkusz Google należy zapodać przez --sheet_id i --sheet_name, a wynik zostanie zapisany w tym samym arkuszu.
    """
    
    if not social and not hours:
        console.print("[bold red]❌ Nie wybrano funkcji. Użyj --help, aby zobaczyć dostępne opcje.[/bold red]")
        click.echo(main.get_help(click.Context(main)))
        return

    # Inicjalizacja Google Sheets Manager
    sheets_manager = GoogleSheetsManager(verbose)

    # Próba wczytania danych z Google Sheets
    try:
        df = sheets_manager.get_google_sheet_as_df(sheet_id, sheet_name, sheet_range)
        console.print(f"[bold green]✅ Wczytano dane z arkusza {sheet_name} (ID: {sheet_id}).[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Błąd przy wczytywaniu danych z arkusza: {e}[/bold red]")
        return

    # Inicjalizacja cache (jeśli wybrano opcję)
    cache = initialize_cache(use_cache)

    # Inicjalizacja klasy przetwarzania danych
    command_manager = CommandManager(df, cache, verbose)

    # Przetwarzanie danych społecznościowych
    if social:
        asyncio.run(command_manager.process_social_data())

    # Przetwarzanie godzin otwarcia
    if hours:
        asyncio.run(command_manager.process_hours())

    # Tworzenie nowego arkusza o nazwie UPD/nazwa_oryginalna
    try:
        new_sheet_name = sheets_manager.create_new_sheet(sheet_id, sheet_name)
    except Exception as e:
        console.print(f"[bold red]❌ Błąd podczas tworzenia nowego arkusza: {e}[/bold red]")
        return

    # Aktualizacja nowego arkusza Google Sheets
    try:
        sheets_manager.update_google_sheet_from_df(sheet_id, new_sheet_name, sheet_range, command_manager.df)
        console.print(f"[bold green]✅ Zaktualizowano dane w nowym arkuszu {new_sheet_name} (ID: {sheet_id}).[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Błąd podczas aktualizacji arkusza: {e}[/bold red]")

    # Zapis cache (jeśli używany)
    if cache:
        cache.save_cache()

if __name__ == "__main__":
    main()