import pytest
from unittest.mock import patch
from main import process_missing_data
import pandas as pd
from asyncio import gather

@pytest.mark.asyncio
@patch("main.search_google")
async def test_async_monitoring(mock_search_google):
    # Mockujemy wynik dla zapytania
    mock_search_google.return_value = "https://example.com/profile"
    
    # Przykładowy DataFrame z brakującymi danymi
    df = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': [0, 0],
        'Facebook': [0, 0]
    })
    
    cache = None
    verbose = True
    
    # Testujemy przetwarzanie zadań asynchronicznych z monitorowaniem
    updated_df, found_count, missing_count = await process_missing_data(df, cache, verbose)

    assert found_count == 4  # Zakładamy, że wszystkie profile zostały znalezione
    assert missing_count == 0  # Brak błędów

    # Sprawdzamy, czy DataFrame został uzupełniony poprawnymi danymi
    assert updated_df['Instagram'].iloc[0] == "https://example.com/profile"
    assert updated_df['Facebook'].iloc[1] == "https://example.com/profile"