from cache import Cache

def test_cache():
    # Inicjalizacja cache
    cache = Cache()
    
    # Test zapisu do cache
    cache.set("test_query", "https://example.com")
    assert cache.get("test_query") == "https://example.com"
    
    # Test zapisu i odczytu innej wartości
    cache.set("another_query", "https://anotherexample.com")
    assert cache.get("another_query") == "https://anotherexample.com"
    
    # Test braku w cache (zwraca None)
    assert cache.get("non_existent_query") is None
    
    # Test nadpisania wartości w cache
    cache.set("test_query", "https://newexample.com")
    assert cache.get("test_query") == "https://newexample.com"
    
    # Usuń test usunięcia wpisu, jeśli ta funkcja nie istnieje