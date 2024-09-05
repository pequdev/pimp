import pytest
from main import process_missing_data
from unittest.mock import patch
import pandas as pd

@pytest.mark.asyncio
@patch("main.search_google")
async def test_process_missing_data(mock_search_google):
    # Mockujemy wynik dla zapytania - wszystkie platformy zwracają linki
    mock_search_google.return_value = {
        'instagram': 'https://instagram.com/example',
        'tiktok': 'https://tiktok.com/example',
        'facebook': 'https://facebook.com/example',
        'youtube': 'https://youtube.com/example',
        'ubereats': 'https://ubereats.com/example',
        'tripadvisor': 'https://tripadvisor.com/example',
        'thefork': 'https://thefork.com/example'
    }
    
    # Przykładowy DataFrame z brakującymi danymi
    df = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Location': ['Location 1', 'Location 2'],  # Dodano lokalizację do zgodności z funkcją
        'Instagram': [0, 0],
        'TikTok': [0, 0],
        'Facebook': [0, 0],
        'YouTube': [0, 0],
        'UberEats': [0, 0],
        'TripAdvisor': [0, 0],
        'TheFork': [0, 0]
    })
    
    # Ustawiamy cache na None
    cache = None
    
    # Uruchamiamy funkcję process_missing_data
    updated_df, found_count, missing_count = await process_missing_data(df, cache, verbose=False)
    
    # Sprawdzamy, czy dane zostały uzupełnione poprawnie dla każdej platformy
    platforms = ['Instagram', 'TikTok', 'Facebook', 'YouTube', 'UberEats', 'TripAdvisor', 'TheFork']
    expected_url = 'https://{}example'
    
    for platform in platforms:
        assert updated_df[platform].iloc[0] == expected_url.format(platform.lower() + '.com/')
        assert updated_df[platform].iloc[1] == expected_url.format(platform.lower() + '.com/')
    
    # Sprawdzamy, czy wartości found_count i missing_count są zgodne
    assert found_count == 2  # Mamy dwa zapytania, każde zwraca poprawne wyniki
    assert missing_count == 0  # Brak brakujących wyników