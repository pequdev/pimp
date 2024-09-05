from main import build_query

def test_build_query():
    assert build_query("The Dickens", "Instagram") == "The Dickens Instagram"
    assert build_query("Bar XYZ", "TikTok") == "Bar XYZ TikTok"