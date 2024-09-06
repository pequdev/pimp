import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
from rich.console import Console

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
    def is_potential_website(link, restaurant_name):
        """Sprawdza, czy link może być stroną domową na podstawie jego hosta."""
        parsed_url = urlparse(link)
        domain_segments = parsed_url.netloc.split('.')

        # Sprawdza, czy nazwa restauracji występuje w domenie
        restaurant_name_words = restaurant_name.lower().split()
        if any(word in parsed_url.netloc.lower() for word in restaurant_name_words):
            return True

        # Sprawdzamy, czy domena ma tylko dwa segmenty (np. lacallaita.es)
        if len(domain_segments) <= 2:
            return True

        return False

    @staticmethod
    async def search_google(query, restaurant_name, verbose=False):
        """Funkcja do wyszukiwania w Google i znajdowania wyników społecznościowych oraz stron domowych."""
        driver = Scraper.initialize_webdriver()

        try:
            search_url = f"https://www.google.es/search?q={query}"
            driver.get(search_url)
            await asyncio.sleep(2)

            # Pobranie źródła strony i parsowanie
            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            # Przetwarzanie linków
            links = soup.find_all('a', href=True)
            social_links = {
                'instagram': None,
                'tiktok': None,
                'facebook': None,
                'youtube': None,
                'tripadvisor': None,
                'thefork': None
            }
            website_link = None

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
                elif 'http' in href and Scraper.is_potential_website(href, restaurant_name):
                    website_link = href

            return {'social_links': social_links, 'website': website_link}

        except Exception as e:
            if verbose:
                console.print(f"Błąd podczas wyszukiwania w Google: {str(e)}", "error")
            return -1
        finally:
            Scraper.close_webdriver(driver)

    @staticmethod
    def initialize_webdriver(headless=True):
        """Inicjalizacja WebDrivera z odpowiednimi opcjami."""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    @staticmethod
    async def get_opening_hours_from_google_maps(google_url, verbose=False):
        """Funkcja do pobierania godzin otwarcia z Google Maps z raportowaniem do konsoli."""
        driver = Scraper.initialize_webdriver()

        try:
            if verbose:
                console.print(f"Pobieranie godzin otwarcia dla: {google_url}")

            driver.get(google_url)

            # Czekanie na pełne załadowanie strony
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            try:
                # Użycie WebDriverWait z oczekiwaniem na element z jsaction zawierającym "openhours"
                open_hours_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[jsaction*="openhours"]'))
                )
    
                # Fetching the parent element
                parent_element = open_hours_button.find_element(By.XPATH, './..')  # Go one level up to the parent
                console.print(f"Parent element: {parent_element.get_attribute('outerHTML')}")  # Log parent element in the console

                # Click on the parent element
                parent_element.click()
                await asyncio.sleep(5)  # Czekamy, aż panel się otworzy

            except Exception as e:
                console.print(f"Błąd podczas klikania przycisku godzin otwarcia: {e}")
                return None

            # Po otwarciu panelu, parsujemy nowy stan strony
            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

            # Znajdujemy godziny otwarcia za pomocą aria-label
            hours_element = soup.find('div', {'aria-label': lambda x: x and 'Hide open hours' in x})
            if hours_element:
                hours_text = hours_element['aria-label']
                console.print(f"Znalezione godziny otwarcia: {hours_text}")
                return hours_text  # Zwracamy godziny otwarcia jako tekst
            else:
                if verbose:
                    console.print(f"Nie udało się znaleźć godzin otwarcia dla {google_url}", "error")

        except Exception as e:
            if verbose:
                console.print(f"Błąd podczas pobierania godzin otwarcia dla {google_url}: {e}", "error")
        finally:
            driver.quit()

        return None