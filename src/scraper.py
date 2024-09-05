from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from rich.console import Console
from rich.tree import Tree
from rich.live import Live
from rich.panel import Panel

console = Console()

async def search_google(query, verbose=False):
    # Uruchomienie ChromeDrivera
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Opcja bez interfejsu graficznego
    driver = webdriver.Chrome(options=options)

    try:
        search_url = f"https://www.google.es/search?q={query}"
        driver.get(search_url)

        # Opcjonalnie: dodaj opóźnienie, aby wyniki miały czas na załadowanie
        time.sleep(2)

        # Pobierz źródło strony
        page_source = driver.page_source

        # Przetwarzanie HTML za pomocą BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Filtrowanie wyników wyszukiwania Google - tylko rzeczywiste wyniki
        search_results = soup.find_all('div', class_='tF2Cxc', limit=5)  # 'tF2Cxc' to klasa div dla wyników wyszukiwania

        # Tworzenie drzewa wyników
        tree = Tree(f"🌐 Wyniki wyszukiwania dla zapytania: '{query}'")

        if search_results:
            for result in search_results:
                # Pobieranie tytułu wyniku
                title = result.find('h3').text if result.find('h3') else "Brak tytułu"
                
                # Pobieranie linku
                link = result.find('a')['href'] if result.find('a') else "Brak linku"

                # Dodawanie do drzewa wyników
                tree.add(f"[blue]{title}[/blue] -> [green]{link}[/green]")
        else:
            tree.add("[red]Brak wyników wyszukiwania[/red]")

        # Wyświetlanie drzewa wyników
        if verbose:
            console.print(Panel(tree, title="Drzewo wyników wyszukiwania", expand=False))

        # Znajdowanie linków społecznościowych na podstawie tych wyników
        links = soup.find_all('a', href=True)
        social_links = {
            'instagram': None,
            'tiktok': None,
            'facebook': None,
            'youtube': None,
            'tripadvisor': None,
            'thefork': None
        }

        for link in links:
            href = link['href']
            if 'instagram.com' in href and not social_links['instagram']:
                social_links['instagram'] = href
            elif 'tiktok.com' in href and not social_links['tiktok']:
                social_links['tiktok'] = href
            elif 'facebook.com' in href and not social_links['facebook']:
                social_links['facebook'] = href
            elif 'youtube.com' in href and not social_links['youtube']:
                social_links['youtube'] = href
            elif 'tripadvisor.com' in href and not social_links['tripadvisor']:
                social_links['tripadvisor'] = href
            elif 'thefork.com' in href and not social_links['thefork']:
                social_links['thefork'] = href

        # Zwracanie znalezionych linków społecznościowych
        return social_links

    except Exception as e:
        if verbose:
            console.print(f"❌ [red]Error during search[/red]: {str(e)}")
        return -1

    finally:
        driver.quit()