from cache import Cache

def test_cache():
    cache = Cache()
    
    # Test zapisu do cache
    cache.set("test_query", "https://example.com")
    assert cache.get("test_query") == "https://example.com"
    
    # Test braku w cache
    assert cache.get("non_existent_query") is None