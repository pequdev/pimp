import pytest
from click.testing import CliRunner
from unittest.mock import patch
from main import main
import pandas as pd

# Mockowanie funkcji pandas.read_csv i process_missing_data dla testów CLI
@patch("pandas.read_csv")
@patch("main.process_missing_data")
def test_dynamic_monitoring(mock_process_missing_data, mock_read_csv):
    # Mockowanie zwracanych danych z pliku CSV
    mock_read_csv.return_value = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': [0, 0],
        'Facebook': [0, 0]
    })

    # Mockowanie wyniku przetwarzania danych
    mock_process_missing_data.return_value = (None, 10, 5)
    
    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social', '--verbose'])
    
    # Sprawdzamy, czy aplikacja wyświetla informację o przetwarzaniu
    assert result.exit_code == 0
    assert "Przetwarzanie danych" in result.output

@patch("pandas.read_csv")
@patch("main.process_missing_data")
def test_cli_without_verbose(mock_process_missing_data, mock_read_csv):
    # Mockowanie zwracanych danych z pliku CSV
    mock_read_csv.return_value = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': [0, 0],
        'Facebook': [0, 0]
    })
    
    # Mockowanie wyniku przetwarzania danych
    mock_process_missing_data.return_value = (None, 10, 0)
    
    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social'])
    
    # Sprawdzamy, czy aplikacja wyświetla podsumowanie
    assert result.exit_code == 0
    assert "Przetworzono rekordy" in result.output