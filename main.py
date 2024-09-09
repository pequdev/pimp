import os
import click
import asyncio
import pandas as pd
import gspread
from concurrent.futures import ProcessPoolExecutor
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from src.process import Process
from src.scraper import Scraper
from src.cache import Cache
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

console = Console()

# Klasa do obsługi Google Sheets
class GoogleSheetsManager:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, verbose=False):
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

    def get_google_sheet_as_df(self, sheet_id, sheet_name):
        """Pobiera dane z Google Sheets jako DataFrame."""
        if self.verbose:
            console.print(f"[yellow]🔄 Pobieranie danych z arkusza Google Sheets o ID: {sheet_id} i nazwie: {sheet_name}[/yellow]")
        
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        
        if self.verbose:
            console.print(f"[bold green]✅ Pobrano dane z arkusza {sheet_name} (ID: {sheet_id})[/bold green]")
        
        return pd.DataFrame(data)

    def update_google_sheet_from_df(self, sheet_id, sheet_name, df):
        """Aktualizuje Google Sheets danymi z DataFrame."""
        if self.verbose:
            console.print(f"[yellow]🔄 Aktualizacja arkusza Google Sheets o ID: {sheet_id} i nazwie: {sheet_name}[/yellow]")
        
        sheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)
        data = df.values.tolist()
        sheet.update(f"A1:Z{len(df) + 1}", data)
        
        if self.verbose:
            console.print(f"[bold green]✅ Pomyślnie zaktualizowano dane w arkuszu {sheet_name} (ID: {sheet_id})[/bold green]")

    def create_new_sheet(self, sheet_id, original_sheet_name):
        """Tworzy nowy arkusz na podstawie oryginalnego arkusza."""
        if self.verbose:
            console.print(f"[yellow]🔄 Tworzenie nowego arkusza: UPD/{original_sheet_name}...[/yellow]")
        
        spreadsheet = self.client.open_by_key(sheet_id)
        new_sheet_name = f"UPD/{original_sheet_name}"
        try:
            spreadsheet.add_worksheet(title=new_sheet_name, rows="1000", cols="26")
            if self.verbose:
                console.print(f"[bold green]✅ Nowy arkusz {new_sheet_name} został utworzony.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Błąd podczas tworzenia nowego arkusza: {e}[/bold red]")
            raise e
        return new_sheet_name


class CommandManager:
    def __init__(self, df, cache, verbose, table, log_panel, layout, live):
        self.df = df
        self.cache = cache
        self.verbose = verbose
        self.table = table
        self.log_panel = log_panel
        self.layout = layout
        self.live = live

    async def process_social_data(self):
        """Przetwarzanie danych społecznościowych."""
        df, found_count, missing_count = await Process.process_social_data(
            self.df, self.cache, self.verbose, self.table, self.log_panel, self.layout, self.live
        )
        return df, found_count, missing_count

    async def process_hours(self, executor):
        """Przetwarzanie godzin otwarcia z multiprocesingiem."""
        loop = asyncio.get_event_loop()
        tasks = []

        for index, row in self.df.iterrows():
            google_url = row['Google']
            if google_url:
                # WebDriver będzie inicjowany w procesie, więc nie przekazujemy layout, live ani WebDrivera.
                task = loop.run_in_executor(
                    executor, Scraper.get_opening_hours_from_google_maps, google_url, self.verbose
                )
                tasks.append(task)

        results = await asyncio.gather(*tasks)
        
        for result, index in zip(results, range(len(self.df))):
            if result:
                self.df.at[index, 'Hours'] = result
        return self.df


def initialize_cache(use_cache):
    """Inicjalizacja cache."""
    if use_cache:
        return Cache()
    return None


@click.command()
@click.option('--sheet_id', required=True, help='ID arkusza Google Sheets z danymi.')
@click.option('--sheet_name', required=True, help='Nazwa arkusza Google Sheets do użycia.')
@click.option('--use_cache', is_flag=True, help='Czy używać cache do przyspieszenia wyszukiwań?')
@click.option('--verbose', is_flag=True, help='Wyświetlaj szczegółowe informacje o przebiegu.')
@click.option('--social', is_flag=True, help='Uzupełniaj brakujące profile społecznościowe.')
@click.option('--hours', is_flag=True, help="Pobierz godziny otwarcia z Google Maps.")
def main(sheet_id, sheet_name, use_cache, verbose, social, hours):
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
        df = sheets_manager.get_google_sheet_as_df(sheet_id, sheet_name)
        console.print(f"[bold green]✅ Wczytano dane z arkusza {sheet_name} (ID: {sheet_id}).[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Błąd przy wczytywaniu danych z arkusza: {e}[/bold red]")
        return

    # Inicjalizacja cache (jeśli wybrano opcję)
    cache = initialize_cache(use_cache)

    # Inicjalizacja layoutu i tabeli
    table = Table(title="Status przetwarzania")
    table.add_column("Nazwa", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center", style="green")
    
    log_panel = Panel("Logi będą się tutaj pojawiać", title="Logi", border_style="magenta")
    
    # Układ dla layoutu
    layout = Layout()
    layout.split_row(
        Layout(table, name="table"),
        Layout(log_panel, name="log")
    )

    async def run_tasks():
        with Live(layout, console=console, refresh_per_second=4) as live:
            command_manager = CommandManager(df, cache, verbose, table, log_panel, layout, live)

            # Przetwarzanie danych społecznościowych
            if social:
                await command_manager.process_social_data()

            # Przetwarzanie godzin otwarcia z multiprocessingiem
            if hours:
                with ProcessPoolExecutor() as executor:
                    # Usunięcie `layout`, `table`, `log_panel` i `live` z wywołań zewnętrznych procesów.
                    await command_manager.process_hours(executor)

        # Tworzenie nowego arkusza o nazwie UPD/nazwa_oryginalna
        try:
            new_sheet_name = sheets_manager.create_new_sheet(sheet_id, sheet_name)
        except Exception as e:
            console.print(f"[bold red]❌ Błąd podczas tworzenia nowego arkusza: {e}[/bold red]")
            return

        # Aktualizacja nowego arkusza Google Sheets
        try:
            sheets_manager.update_google_sheet_from_df(sheet_id, new_sheet_name, command_manager.df)
            console.print(f"[bold green]✅ Zaktualizowano dane w nowym arkuszu {new_sheet_name} (ID: {sheet_id}).[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Błąd podczas aktualizacji arkusza: {e}[/bold red]")

        # Zapis cache (jeśli używany)
        if cache:
            cache.save_cache()

    # Uruchomienie zadań w ramach jednej sesji asyncio
    asyncio.run(run_tasks())

if __name__ == "__main__":
    main()