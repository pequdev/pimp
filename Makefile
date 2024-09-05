# Makefile do automatycznej konfiguracji środowiska, instalacji zależności i konfiguracji ChromeDriver

# Tworzenie i aktywacja wirtualnego środowiska
venv:
	python3 -m venv venv
	. venv/bin/activate

# Instalacja zależności w wirtualnym środowisku
install: venv
	venv/bin/pip install -r requirements.txt

# Instalacja ChromeDriver za pomocą Homebrew
chromedriver:
	@if ! command -v chromedriver &> /dev/null; then \
		echo "Instalacja ChromeDriver za pomocą Homebrew..."; \
		brew install chromedriver; \
	else \
		echo "ChromeDriver już zainstalowany."; \
	fi