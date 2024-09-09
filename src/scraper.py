import os
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console

console = Console()

class Scraper:

    @staticmethod
    def initialize_webdriver(headless=True):
        """Inicjalizacja WebDrivera z odpowiednimi opcjami oraz symulowaną geolokalizacją."""
        options = Options()

        latitude = 38.34486
        longitude = 0.48550
        accuracy = 100

        if headless:
            options.add_argument('--headless=new')

        options.add_argument("--disable-first-run-ui")
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        profile_path = os.path.join(parent_dir, 'data/chrome_profile')
        options.add_argument(f"--user-data-dir={profile_path}")

        options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.images': 2,
            'intl.accept_languages': 'en,en_US'
        })

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            })
            return driver
        except Exception as e:
            console.print(f"Błąd inicjalizacji WebDrivera: {e}")
            return None

    @staticmethod
    def close_webdriver(driver):
        """Zamyka WebDrivera."""
        if driver:
            driver.quit()

    @staticmethod
    def _check_consent_cookie(driver):
        """Sprawdza, czy zgoda na cookies została już zapisana w plikach cookies przeglądarki."""
        cookies = driver.get_cookies()
        consent_cookies = [cookie for cookie in cookies if "CONSENT" in cookie['name']]
        if consent_cookies:
            console.print("[blue]Zgoda na cookies już zapisana.[/blue]")
            return True
        return False

    @staticmethod
    def _handle_google_consent(driver, verbose=False):
        """Obsługuje zgodę na pliki cookies w Google w różnych językach."""
        if Scraper._check_consent_cookie(driver):
            return

        consent_text_variants = [
            'Alle akzeptieren', 'Zaakceptuj wszystko', 'Akceptuj wszystkie', 
            'Accept all', 'Aceptar todo'
        ]
        for variant in consent_text_variants:
            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{variant}')]"))
                )
                parent_button = element.find_element(By.XPATH, './ancestor::button')
                parent_button.click()
                if verbose:
                    console.print(f"[blue]Kliknięto przycisk zgody: {variant}[/blue]")
                return True
            except Exception:
                if verbose:
                    console.print(f"[yellow]Brak przycisku zgody z tekstem: {variant}[/yellow]")
        return False

    @staticmethod
    def parse_page(html_content):
        """Parsuje stronę HTML za pomocą BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')

    @staticmethod
    def is_potential_website(link, restaurant_name):
        """Sprawdza, czy link może być stroną domową na podstawie jego hosta."""
        parsed_url = urlparse(link)
        domain_segments = parsed_url.netloc.split('.')

        restaurant_name_words = restaurant_name.lower().split()
        if any(word in parsed_url.netloc.lower() for word in restaurant_name_words):
            return True

        if len(domain_segments) <= 2:
            return True

        return False

    @staticmethod
    def sort_hours(hours_text):
        """Funkcja do wykrywania języka i sortowania godzin otwarcia od poniedziałku do niedzieli."""
        days_of_week = {
            'PL': ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'],
            'EN': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'DE': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
            'ES': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        }

        detected_language = None
        for lang, days in days_of_week.items():
            if any(day in hours_text for day in days):
                detected_language = lang
                break

        if detected_language is None:
            raise ValueError("Nie udało się rozpoznać języka z godzin otwarcia.")
        
        hours_list = re.findall(r'(\w+),(.*?)(?=;|$)', hours_text)
        day_to_index = {day: index for index, day in enumerate(days_of_week[detected_language])}
        sorted_hours = sorted(hours_list, key=lambda x: day_to_index.get(x[0], -1))
        sorted_hours_text = "; ".join([f"{day},{hours.strip()}" for day, hours in sorted_hours])

        return sorted_hours_text

    @staticmethod
    def get_opening_hours_from_google_maps(google_url, verbose=False):
        """Pobieranie godzin otwarcia z Google Maps."""
        driver = Scraper.initialize_webdriver()

        try:
            if verbose:
                console.print(f"Pobieranie godzin otwarcia dla: {google_url}")

            driver.get(google_url)

            # Obsługa zgody na cookies
            Scraper._handle_google_consent(driver, verbose)

            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            try:
                # Wyszukiwanie elementu z godzinami otwarcia
                language_variants = [
                    'Hide open hours',           # English
                    'Ukryj godziny otwarcia',    # Polish
                    'Öffnungszeiten für die Woche ausblenden',  # German
                    'Ocultar horas de apertura'  # Spanish
                ]

                hours_element = None
                for variant in language_variants:
                    try:
                        hours_element = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f'div[aria-label*="{variant}"]'))
                        )
                        if hours_element:
                            break
                    except Exception:
                        continue

                if not hours_element:
                    if verbose:
                        console.print(f"[red]Nie znaleziono elementu z godzinami otwarcia.[/red]")
                    return None

                hours_text = hours_element.get_attribute('aria-label')
                if verbose:
                    console.print(f"[bold green]Znaleziono godziny otwarcia: {hours_text}[/bold green]")

                # Usunięcie niepotrzebnych fraz i sortowanie godzin
                phrases_to_remove = [
                    'Öffnungszeiten für die Woche ausblenden',  # German
                    'Hide open hours for the week',             # English
                    'Ukryj godziny otwarcia na cały tydzień',   # Polish
                    'Ocultar horas de apertura para la semana'  # Spanish
                ]
                for phrase in phrases_to_remove:
                    hours_text = hours_text.replace(phrase, '').strip()

                sorted_hours_text = Scraper.sort_hours(hours_text)

                if verbose:
                    console.print(f"[bold green]Posortowane godziny: {sorted_hours_text}[/bold green]")

                return sorted_hours_text

            except Exception as e:
                if verbose:
                    console.print(f"[red]Błąd podczas pobierania godzin otwarcia: {e}[/red]")
                return None

        except Exception as e:
            if verbose:
                console.print(f"[red]Błąd ładowania danych z {google_url}: {e}[/red]")
            return None

        finally:
            Scraper.close_webdriver(driver)

        return None