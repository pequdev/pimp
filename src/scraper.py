from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio

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
        """Funkcja do wyszukiwania w Google i znajdowania wyników społecznościowych oraz strony domowej."""
        driver = Scraper.initialize_webdriver()

        try:
            search_url = f"https://www.google.es/search?q={query}"
            driver.get(search_url)

            await asyncio.sleep(2)

            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            # Filtrowanie wyników wyszukiwania Google
            search_results = soup.find_all('div', class_='tF2Cxc', limit=20)

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
            website_link = None  # Zmienna do przechowywania strony domowej

            if search_results:
                for result in search_results:
                    title = result.find('h3').text if result.find('h3') else "Brak tytułu"
                    link_element = result.find('a')

                    # Sprawdzenie, czy link istnieje
                    if link_element and link_element['href']:
                        link = link_element['href']
                        if verbose:
                            console.log(f"Znaleziono link: {link}")

                        # Sprawdzamy, czy link jest prawidłowym URL
                        if Scraper.is_valid_url(link):
                            if verbose:
                                console.log(f"Link jest prawidłowy: {link}")

                            # Ignorowanie linków do recenzji, takich jak TripAdvisor
                            if any(platform in link for platform in ['tripadvisor.com', 'yelp.com']):
                                if verbose:
                                    console.log(f"Ignorowanie linku do recenzji: {link}")
                                continue
                        else:
                            link = None
                            if verbose:
                                console.log(f"Link nie jest prawidłowy: {title}")
                    else:
                        link = None
                        if verbose:
                            console.log(f"Brak linku dla wyników wyszukiwania: {title}")

                    # Wyświetlanie wyniku w tabeli
                    if verbose and link:
                        table.add_row(title, link)

                    # Sprawdzenie linków społecznościowych tylko wtedy, gdy link istnieje i jest typu str
                    if isinstance(link, str):
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

                        # Jeśli link wygląda na stronę domową, przypisujemy go do `website_link`
                        if 'http' in link and not any(platform for platform in social_links.values() if platform) and Scraper.is_potential_website(link):
                            website_link = link  # Zakładamy, że to strona domowa
                    elif verbose:
                        console.log(f"Link jest None lub nie jest stringiem: {link}")

            if verbose:
                console.print(table)

            # Zwracanie znalezionych linków społecznościowych i strony domowej
            return {
                'social_links': social_links,
                'website': website_link
            }

        except Exception as e:
            Scraper.report(f"Błąd podczas wyszukiwania w Google: {e}", "error")
            return -1
        finally:
            Scraper.close_webdriver(driver)

    @staticmethod
    def is_valid_url(url):
        """Sprawdza, czy URL jest prawidłowy."""
        return url and (url.startswith('http://') or url.startswith('https://'))

    @staticmethod
    def is_potential_website(link):
        """Funkcja do oceny, czy link jest potencjalną stroną domową."""
        # Rozkładamy URL na elementy
        parsed_url = urlparse(link)

        # Sprawdzamy, czy domena ma tylko dwa segmenty (np. lacallaita.es)
        domain_segments = parsed_url.netloc.split('.')
        if len(domain_segments) <= 2:
            return True

        # Dodatkowe sprawdzenie, czy URL ma krótką ścieżkę (nie jest subdomeną lub podstroną)
        if len(parsed_url.path.split('/')) <= 2:
            return True

        return False

    @staticmethod
    async def get_opening_hours(google_url, verbose=False):
        """Funkcja do pobierania godzin otwarcia z Google Maps z raportowaniem do konsoli."""
        driver = Scraper.initialize_webdriver()

        try:
            if verbose:
                Scraper.report(f"Pobieranie godzin otwarcia dla: {google_url}")

            driver.get(google_url)
            await asyncio.sleep(3)

            # Parsowanie strony za pomocą BeautifulSoup
            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            # Znajdowanie godzin otwarcia przy użyciu BeautifulSoup
            hours_data = None
            hours_element = soup.find('div', class_='hours-class')  # Weryfikacja struktury HTML
            if hours_element:
                hours_data = hours_element.text
                if verbose:
                    Scraper.report(f"Znalezione godziny otwarcia: {hours_data}", "success")
            else:
                if verbose:
                    Scraper.report(f"Nie udało się znaleźć godzin otwarcia dla {google_url}", "error")

        except Exception as e:
            if verbose:
                Scraper.report(f"Błąd podczas pobierania godzin otwarcia dla {google_url}: {e}", "error")
            hours_data = None
        finally:
            driver.quit()

        return hours_data