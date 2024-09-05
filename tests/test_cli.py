import pytest
from click.testing import CliRunner
from main import main
from unittest.mock import patch

# Test sprawdzający, czy aplikacja wyświetla dynamicznie monitorowanie zadań
@patch("main.process_missing_data")
def test_dynamic_monitoring(mock_process_missing_data, mocker):
    # Mockujemy funkcję process_missing_data
    mock_process_missing_data.return_value = (None, 10, 5)
    
    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social', '--verbose'])
    
    # Sprawdzamy, czy progres bar oraz informacja o przetwarzaniu są wyświetlane
    assert result.exit_code == 0
    assert "Przetwarzanie danych" in result.output
    assert "Zakończono" in result.output or "Błąd" in result.output

# Test CLI bez verbose
def test_cli_without_verbose(mocker):
    mocker.patch('main.process_missing_data', return_value=(None, 10, 0))
    
    runner = CliRunner()
    result = runner.invoke(main, ['--input_file', 'data/test.csv', '--social'])
    
    # Sprawdzamy, czy po zakończeniu działania aplikacji wyświetla się podsumowanie
    assert result.exit_code == 0
    assert "Przetworzono rekordy" in result.output