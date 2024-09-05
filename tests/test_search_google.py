import pytest
from main import process_missing_data
from unittest.mock import patch

@pytest.mark.asyncio
@patch("main.search_google")
async def test_process_missing_data(mock_search_google):
    # Mockujemy wynik dla zapytania
    mock_search_google.return_value = "https://instagram.com/example"
    
    # Przykładowy DataFrame z brakującymi danymi
    import pandas as pd
    df = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Instagram': [0, 0],
        'Facebook': [0, 0]
    })
    
    # Ustawiamy cache na None
    cache = None
    
    # Uruchamiamy funkcję process_missing_data
    updated_df, found_count, missing_count = await process_missing_data(df, cache, verbose=False)
    
    # Sprawdzamy, czy dane zostały uzupełnione
    assert updated_df['Instagram'].iloc[0] == "https://instagram.com/example"
    assert updated_df['Instagram'].iloc[1] == "https://instagram.com/example"
    assert found_count == 2
    assert missing_count == 0