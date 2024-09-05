from main import build_query

def test_build_query():
    # Testowanie budowania zapytania z nazwą restauracji i platformą
    assert build_query("The Dickens", "Instagram") == "The Dickens Instagram"
    assert build_query("Bar XYZ", "TikTok") == "Bar XYZ TikTok"
    
    # Dodajemy lokalizację do zapytań
    assert build_query("The Dickens", "New York") == "The Dickens New York"
    assert build_query("La Guapa", "Alicante") == "La Guapa Alicante"
    
    # Testowanie budowania zapytań z różnymi nazwami i lokalizacjami
    assert build_query("Bar ABC", "Facebook") == "Bar ABC Facebook"
    assert build_query("Cafe 123", "Los Angeles") == "Cafe 123 Los Angeles"