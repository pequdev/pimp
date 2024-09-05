import json
import os
from rich.console import Console

console = Console()

class Cache:
    def __init__(self, cache_file='data/cache.json'):
        self.cache_file = cache_file
        self.data = self.load_cache()

    def load_cache(self):
        """Ładowanie cache z pliku."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as file:
                    console.print(f"🔄 [yellow]Ładowanie cache z {self.cache_file}[/yellow]")
                    return json.load(file)
            except json.JSONDecodeError:
                console.print(f"❌ [red]Błąd odczytu pliku cache. Plik może być uszkodzony.[/red]")
                return {}
            except Exception as e:
                console.print(f"❌ [red]Błąd podczas ładowania cache: {e}[/red]")
                return {}
        else:
            console.print(f"⚠️ [yellow]Plik cache nie istnieje, utworzono nowy cache.[/yellow]")
        return {}

    def save_cache(self):
        """Zapisanie cache do pliku."""
        try:
            # Sprawdzamy, czy katalog istnieje, jeśli nie - tworzymy go
            cache_dir = os.path.dirname(self.cache_file)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                console.print(f"📁 [yellow]Utworzono katalog {cache_dir} dla pliku cache.[/yellow]")

            with open(self.cache_file, 'w') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
                console.print(f"💾 [green]Zapisano cache do {self.cache_file}[/green]")
        except Exception as e:
            console.print(f"❌ [red]Błąd podczas zapisu cache: {e}[/red]")

    def get(self, query):
        """Pobieranie danych z cache."""
        result = self.data.get(query)
        if result is None:
            console.print(f"⚠️ [yellow]Brak danych w cache dla zapytania: {query}[/yellow]")
        return result

    def set(self, query, result):
        """Ustawianie wartości w cache."""
        self.data[query] = result
        console.print(f"🔑 [blue]Dodano do cache: {query}[/blue]")