import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import re
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
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-infobars')  # Usuwa pasek informacyjny
        options.add_argument('--disable-extensions')  # Wyłącza rozszerzenia
        options.add_argument('--start-maximized')  # Maksymalizuje okno
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-blink-features=AutomationControlled')  # Ukrywa fakt, że Selenium kontroluje przeglądarkę
        options.add_argument('--lang=en')  # Ustawienie języka, można zmienić na PL lub DE w zależności od potrzeby

        # Dodatkowe opcje, które mogą pomóc
        prefs = {
            'profile.default_content_setting_values.cookies': 2,  # Blokuj ciasteczka
            'profile.default_content_setting_values.images': 2,  # Blokuj obrazy (optymalizacja)
            'intl.accept_languages': 'en,en_US'  # Ustawienia językowe
        }
        options.add_experimental_option('prefs', prefs)

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
    def sort_hours(hours_text):
        """Funkcja do wykrywania języka i sortowania godzin otwarcia od poniedziałku do niedzieli."""
        
        # Mapa dni tygodnia w różnych językach
        days_of_week = {
            'PL': ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'],
            'EN': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'DE': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
            'ES': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        }
        
        # Detekcja języka na podstawie pierwszego pasującego dnia tygodnia
        detected_language = None
        for lang, days in days_of_week.items():
            if any(day in hours_text for day in days):
                detected_language = lang
                break

        if detected_language is None:
            raise ValueError("Nie udało się rozpoznać języka z godzin otwarcia.")
        
        # Wyodrębnienie wszystkich dni i godzin przy pomocy wyrażenia regularnego
        hours_list = re.findall(r'(\w+),(.*?)(?=;|$)', hours_text)
        
        # Mapa dni tygodnia na numery (indeksy) do sortowania
        day_to_index = {day: index for index, day in enumerate(days_of_week[detected_language])}

        # Sortowanie godzin na podstawie indeksów dni tygodnia
        sorted_hours = sorted(hours_list, key=lambda x: day_to_index.get(x[0], -1))

        # Składanie wyników w odpowiednim formacie
        sorted_hours_text = "; ".join([f"{day},{hours.strip()}" for day, hours in sorted_hours])

        return sorted_hours_text

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
    async def get_opening_hours_from_google_maps(google_url, verbose=False):
        """Funkcja do pobierania godzin otwarcia z Google Maps z raportowaniem do konsoli."""
        driver = Scraper.initialize_webdriver(headless=True)

        try:
            if verbose:
                console.print(f"Pobieranie godzin otwarcia dla: {google_url}")

            driver.get(google_url)

            # Czekanie na pełne załadowanie strony
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # Symulacja naciśnięcia TAB i ENTER, aby akceptować pliki cookie
            try:
                body = driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.TAB * 4)  # W zależności od struktury strony może być konieczna zmiana liczby TAB
                body.send_keys(Keys.ENTER)
                await asyncio.sleep(2)  # Czekamy, aby upewnić się, że strona się odświeża po kliknięciu
                if verbose:
                    console.print("[bold blue]Symulowano kliknięcie przycisku zgody na pliki cookie.[/bold blue]")
            except Exception as e:
                if verbose:
                    console.print("[yellow]Nie udało się symulować kliknięcia przycisku zgody na pliki cookie.[/yellow]")

            # Dalsza część kodu scrapującego
            try:
                # Różne wersje językowe frazy "Hide open hours"
                language_variants = [
                    'Hide open hours',           # EN
                    'Ukryj godziny otwarcia',    # PL
                    'Öffnungszeiten für die Woche ausblenden', # DE
                    'Ocultar horas de apertura'  # ES
                ]

                # Tworzenie selektorów CSS dla każdej wersji językowej
                hours_element = None
                for variant in language_variants:
                    try:
                        hours_element = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f'div[aria-label*="{variant}"]'))
                        )
                        if hours_element:
                            break  # Znaleziono element, nie trzeba kontynuować
                    except Exception:
                        continue  # Próbujemy kolejny język, jeśli nie znaleziono elementu

                if not hours_element:
                    console.print("[red]Nie znaleziono elementu z aria-label w żadnej wersji językowej.[/red]")
                    return None

                if verbose:
                    console.print(f"[bold blue]Znaleziony element z aria-label: {hours_element}[/bold blue]")

                # Pobieramy wartość aria-label
                hours_text = hours_element.get_attribute('aria-label')

                if verbose:
                    console.print(f"[bold green]Znalezione godziny otwarcia: {hours_text}[/bold green]")

                # Usuwamy frazy typu "Hide open hours" lub odpowiedników w innych językach
                phrases_to_remove = [
                    'Öffnungszeiten für die Woche ausblenden',  # DE
                    'Hide open hours for the week',             # EN
                    'Ukryj godziny otwarcia na cały tydzień',   # PL
                    'Ocultar horas de apertura para la semana'  # ES
                ]
                for phrase in phrases_to_remove:
                    hours_text = hours_text.replace(phrase, '').strip()

                # Sortujemy dni tygodnia według odpowiedniego języka
                sorted_hours_text = Scraper.sort_hours(hours_text)

                return sorted_hours_text

            except Exception as e:
                console.print(f"Błąd podczas pobierania godzin otwarcia: {e}")
                return None

        except Exception as e:
            if verbose:
                console.print(f"Błąd podczas pobierania danych dla {google_url}: {e}", "error")
        finally:
            driver.quit()

        return None