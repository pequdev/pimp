import pytest
from click.testing import CliRunner
from unittest.mock import patch
from main import main
import pandas as pd

@patch("pandas.read_csv")
@patch("main.process_missing_data")
def test_dynamic_monitoring(mock_process_missing_data, mock_read_csv):
    # Mockowanie zwracanych danych z pliku CSV
    mock_read_csv.return_value = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Location': ['Location 1', 'Location 2'],  # Dodaj lokalizację, jeśli potrzebna
        'Instagram': [0, 0],
        'TikTok': [0, 0],
        'Facebook': [0, 0],
        'YouTube': [0, 0],
        'UberEats': [0, 0],
        'TripAdvisor': [0, 0],
        'TheFork': [0, 0]
    })

    # Mockowane dane zwracane przez process_missing_data
    mock_process_missing_data.return_value = (pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': ['https://instagram.com/bar1', 'https://instagram.com/bar2'],
        'Facebook': ['https://facebook.com/bar1', 'https://facebook.com/bar2'],
        'TikTok': ['https://tiktok.com/bar1', 'https://tiktok.com/bar2'],
        'YouTube': ['https://youtube.com/bar1', 'https://youtube.com/bar2'],
        'UberEats': ['https://ubereats.com/bar1', 'https://ubereats.com/bar2'],
        'TripAdvisor': ['https://tripadvisor.com/bar1', 'https://tripadvisor.com/bar2'],
        'TheFork': ['https://thefork.com/bar1', 'https://thefork.com/bar2']
    }), 2, 0)

    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social', '--verbose'])

    # Sprawdzamy, czy aplikacja wyświetla podsumowanie
    assert result.exit_code == 0
    assert "✅ Przetworzono 2 znalezionych rekordów i 0 brakujących." in result.output

@patch("pandas.read_csv")
@patch("main.process_missing_data")
def test_cli_without_verbose(mock_process_missing_data, mock_read_csv):
    # Mockowanie zwracanych danych z pliku CSV
    mock_read_csv.return_value = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': [0, 0],
        'Facebook': [0, 0]
    })
    
    # Zwracamy DataFrame, który aplikacja zapisze do pliku CSV
    mock_process_missing_data.return_value = (pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': ['https://instagram.com/bar1', 'https://instagram.com/bar2'],
        'Facebook': ['https://facebook.com/bar1', 'https://facebook.com/bar2'],
        'TikTok': ['https://tiktok.com/bar1', 'https://tiktok.com/bar2'],
        'YouTube': ['https://youtube.com/bar1', 'https://youtube.com/bar2'],
        'UberEats': ['https://ubereats.com/bar1', 'https://ubereats.com/bar2'],
        'TripAdvisor': ['https://tripadvisor.com/bar1', 'https://tripadvisor.com/bar2'],
        'TheFork': ['https://thefork.com/bar1', 'https://thefork.com/bar2']
    }), 2, 0)  # Zwracamy 2 znalezione wyniki
    
    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social'])
    
    # Sprawdzamy, czy aplikacja wyświetla podsumowanie
    assert result.exit_code == 0
    assert "ℹ️ Przetworzono rekordy: 2 znalezionych, 0 brakujących" in result.output