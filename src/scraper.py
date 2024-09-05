from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

console = Console()

class Scraper:
    
    @staticmethod
    def initialize_webdriver(headless=True):
        """Inicjalizacja WebDrivera z odpowiednimi opcjami."""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    @staticmethod
    def close_webdriver(driver):
        """Zamyka WebDrivera."""
        if driver:
            driver.quit()

    @staticmethod
    def parse_page(html_content):
        """Metoda do parsowania HTML za pomocą BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')

    @staticmethod
    def report(message, status="info"):
        """Unified method for reporting to console using rich."""
        if status == "info":
            console.print(f"ℹ️  {message}")
        elif status == "success":
            console.print(f"[green]✅  {message}[/green]")
        elif status == "error":
            console.print(f"[red]❌  {message}[/red]")
        else:
            console.print(message)

    @staticmethod
    async def search_google(query, verbose=False):
        """Funkcja do wyszukiwania w Google i znajdowania wyników społecznościowych."""
        driver = Scraper.initialize_webdriver()

        try:
            search_url = f"https://www.google.es/search?q={query}"
            driver.get(search_url)

            await asyncio.sleep(2)

            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            search_results = soup.find_all('div', class_='tF2Cxc', limit=5)

            if verbose:
                table = Table(title=f"Wyniki wyszukiwania dla zapytania: {query}", show_lines=True)
                table.add_column("Tytuł", justify="left")
                table.add_column("Link", justify="left")

            social_links = {
                'instagram': None,
                'tiktok': None,
                'facebook': None,
                'youtube': None,
                'tripadvisor': None,
                'thefork': None
            }

            if search_results:
                for result in search_results:
                    title = result.find('h3').text if result.find('h3') else "Brak tytułu"
                    link = result.find('a')['href'] if result.find('a') else "Brak linku"
                    
                    if verbose:
                        table.add_row(title, link)

                    if 'instagram.com' in link:
                        social_links['instagram'] = link
                    elif 'tiktok.com' in link:
                        social_links['tiktok'] = link
                    elif 'facebook.com' in link:
                        social_links['facebook'] = link
                    elif 'youtube.com' in link:
                        social_links['youtube'] = link
                    elif 'tripadvisor.com' in link:
                        social_links['tripadvisor'] = link
                    elif 'thefork.com' in link:
                        social_links['thefork'] = link

            if verbose:
                console.print(table)

            return social_links

        except Exception as e:
            Scraper.report(f"Błąd podczas wyszukiwania w Google: {e}", "error")
            return -1
        finally:
            Scraper.close_webdriver(driver)

    @staticmethod
    async def get_opening_hours(google_url, verbose=False):
        """Funkcja do pobierania godzin otwarcia z Google Maps."""
        driver = Scraper.initialize_webdriver()

        try:
            if verbose:
                Scraper.report(f"Pobieranie godzin otwarcia dla: {google_url}")

            driver.get(google_url)
            await asyncio.sleep(3)

            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            hours_element = soup.find('div', class_='hours-class')
            hours_data = hours_element.text if hours_element else None

            if hours_data:
                Scraper.report(f"Znalezione godziny otwarcia: {hours_data}", "success")
            else:
                Scraper.report(f"Nie znaleziono godzin otwarcia dla {google_url}", "error")

            return hours_data

        except Exception as e:
            Scraper.report(f"Błąd podczas pobierania godzin otwarcia dla {google_url}: {e}", "error")
            return None
        finally:
            Scraper.close_webdriver(driver)