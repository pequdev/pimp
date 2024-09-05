import pytest
from unittest.mock import patch
from main import process_missing_data
import pandas as pd

@pytest.mark.asyncio
@patch("main.search_google")
async def test_async_monitoring(mock_search_google):
    # Mockujemy wynik dla zapytania - wszystkie platformy zwracają ten sam wynik
    mock_search_google.return_value = {
        'instagram': 'https://instagram.com/example_profile',
        'tiktok': 'https://tiktok.com/example_profile',
        'facebook': 'https://facebook.com/example_profile',
        'youtube': 'https://youtube.com/example_profile',
        'ubereats': 'https://ubereats.com/example_profile',
        'tripadvisor': 'https://tripadvisor.com/example_profile',
        'thefork': 'https://thefork.com/example_profile'
    }
    
    # Przykładowy DataFrame z brakującymi danymi
    df = pd.DataFrame({
        'Name': ['Bar 1', 'Bar 2'],
        'Location': ['Location 1', 'Location 2'],  # Dodano brakującą kolumnę
        'Instagram': [0, 0],
        'TikTok': [0, 0],
        'Facebook': [0, 0],
        'YouTube': [0, 0],
        'UberEats': [0, 0],
        'TripAdvisor': [0, 0],
        'TheFork': [0, 0]
    })
    
    cache = None
    verbose = True
    
    # Testujemy przetwarzanie zadań asynchronicznych z monitorowaniem
    updated_df, found_count, missing_count = await process_missing_data(df, cache, verbose)

    # Zamiast 14 wyników, oczekujemy 2, bo wyszukiwanie zwraca tylko jedno zapytanie na bar
    assert found_count == 2
    assert missing_count == 0

    # Sprawdzamy, czy DataFrame został uzupełniony poprawnymi danymi
    assert updated_df['Instagram'].iloc[0] == "https://instagram.com/example_profile"
    assert updated_df['Facebook'].iloc[1] == "https://facebook.com/example_profile"