# Makefile do automatycznej konfiguracji środowiska, instalacji zależności, konfiguracji ChromeDriver i czyszczenia cache

VENV_DIR := venv
REQUIREMENTS := requirements.txt
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Tworzenie i aktywacja wirtualnego środowiska
venv:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

# Instalacja zależności w wirtualnym środowisku
install: venv
	$(PIP) install -r $(REQUIREMENTS)

# Sprawdzenie, czy requirements.txt został zmodyfikowany i aktualizacja zależności
update_venv: venv
	@if [ $(REQUIREMENTS) -nt $(VENV_DIR) ]; then \
		echo "Zmieniono requirements.txt, aktualizacja zależności..."; \
		$(PIP) install -r $(REQUIREMENTS); \
	else \
		echo "Środowisko venv jest aktualne."; \
	fi

# Usuwanie starego wirtualnego środowiska
clean_venv:
	rm -rf $(VENV_DIR)

# Usuwanie cache Pythona
clean_cache:
	@echo "Usuwanie katalogów __pycache__ ..."
	find . -name "__pycache__" -type d -exec rm -r {} +

# Instalacja ChromeDriver za pomocą Homebrew
chromedriver:
	@if ! command -v chromedriver &> /dev/null; then \
		echo "Instalacja ChromeDriver za pomocą Homebrew..."; \
		brew install chromedriver; \
	else \
		echo "ChromeDriver już zainstalowany."; \
	fi

# Wejście do wirtualnego środowiska
activate:
	@echo "Wejdź do środowiska: source $(VENV_DIR)/bin/activate"

# Wyświetlenie pomocy
help:
	@echo "Dostępne komendy:"
	@echo "  make venv         - Tworzy wirtualne środowisko"
	@echo "  make install      - Instaluje zależności"
	@echo "  make update_venv  - Aktualizuje zależności po zmianie requirements.txt"
	@echo "  make clean_venv   - Usuwa stare środowisko venv"
	@echo "  make clean_cache  - Usuwa katalogi __pycache__"
	@echo "  make chromedriver - Instaluje ChromeDriver"
	@echo "  make activate     - Wyświetla polecenie do wejścia w środowisko"