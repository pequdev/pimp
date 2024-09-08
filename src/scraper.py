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
import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

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
            options.add_argument('--headless=new')  # Nowa wersja headless

        # Wyłączenie okna pierwszego uruchomienia
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

            driver.execute_cdp_cmd(
                "Emulation.setGeolocationOverride", {
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy
                }
            )
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
    def parse_page(html_content):
        """Metoda do parsowania HTML za pomocą BeautifulSoup."""
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
    async def search_google(query, restaurant_name, table, log_panel, layout, live, verbose=False):
        """Funkcja do wyszukiwania w Google i znajdowania wyników społecznościowych oraz stron domowych."""
        driver = Scraper.initialize_webdriver()

        try:
            search_url = f"https://www.google.es/search?q={query}"
            driver.get(search_url)
            await asyncio.sleep(2)

            page_source = driver.page_source
            soup = Scraper.parse_page(page_source)

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

            if verbose:
                log_panel.title = f"✅ Zakończono wyszukiwanie dla: {restaurant_name}"
                layout['log'].update(log_panel)
                live.update(layout)

            return {'social_links': social_links, 'website': website_link}

        except Exception as e:
            if verbose:
                log_panel = Panel(f"Błąd podczas wyszukiwania w Google: {str(e)}", title="Logi", border_style="red")
            return -1
        finally:
            Scraper.close_webdriver(driver)

    @staticmethod
    async def get_opening_hours_from_google_maps(google_url, table, log_panel, layout, live, verbose=False):
        """Funkcja do pobierania godzin otwarcia z Google Maps z raportowaniem do konsoli."""
        driver = Scraper.initialize_webdriver()

        try:
            if verbose:
                log_panel = Panel(f"Pobieranie godzin otwarcia dla: {google_url}", title="Logi", border_style="magenta")
                layout['log'].update(log_panel)
                live.update(layout)
                
            driver.get(google_url)

            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            if verbose:
                page_source = driver.page_source
                soup = Scraper.parse_page(page_source)
                log_panel = Panel(soup.body.prettify(), title="HTML Tree", border_style="cyan")
                layout['log'].update(log_panel)
                live.update(layout)

            try:
                consent_text_variants = [
                    'Alle akzeptieren',       # German
                    'Zaakceptuj wszystko',    # Polish
                    'Akceptuj wszystkie',     # Polish (alternative)
                    'Accept all',             # English
                    'Aceptar todo'            # Spanish
                ]

                for variant in consent_text_variants:
                    try:
                        element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{variant}')]"))
                        )
                        parent_button = element.find_element(By.XPATH, './ancestor::button')
                        parent_button.click()
                        await asyncio.sleep(2)
                        if verbose:
                            log_panel = Panel(f"[bold blue]Clicked consent button: {variant}[/bold blue]", title="Logi", border_style="green")
                            layout['log'].update(log_panel)
                            live.update(layout)
                        break
                    except Exception:
                        if verbose:
                            log_panel = Panel(f"[yellow]Consent button with text '{variant}' not found, trying next...[/yellow]", title="Logi", border_style="yellow")
                            layout['log'].update(log_panel)
                            live.update(layout)

            except Exception as e:
                if verbose:
                    log_panel = Panel(f"[yellow]Error clicking consent button: {e}[/yellow]", title="Logi", border_style="red")
                    layout['log'].update(log_panel)
                    live.update(layout)

            try:
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
                    log_panel = Panel("[red]No element found with aria-label for open hours in any language.[/red]", title="Logi", border_style="red")
                    layout['log'].update(log_panel)
                    live.update(layout)
                    return None

                hours_text = hours_element.get_attribute('aria-label')
                if verbose:
                    log_panel = Panel(f"[bold green]Found opening hours: {hours_text}[/bold green]", title="Logi", border_style="green")
                    layout['log'].update(log_panel)
                    live.update(layout)

                # Remove unwanted phrases and sort hours
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
                    log_panel = Panel(f"[bold green]Sorted hours: {sorted_hours_text}[/bold green]", title="Logi", border_style="green")
                    layout['log'].update(log_panel)
                    live.update(layout)

                return sorted_hours_text

            except Exception as e:
                log_panel = Panel(f"[red]Error fetching opening hours: {e}[/red]", title="Logi", border_style="red")
                layout['log'].update(log_panel)
                live.update(layout)
                return None

        except Exception as e:
            if verbose:
                log_panel = Panel(f"[red]Error loading data for {google_url}: {e}[/red]", title="Logi", border_style="red")
                layout['log'].update(log_panel)
                live.update(layout)
        finally:
            Scraper.close_webdriver(driver)

        return None