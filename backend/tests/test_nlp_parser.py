from app.ai.nlp_parser import nlp_parser


def test_language_detection():
    assert nlp_parser.detect_language("Kal Amritsar mein baarish hogi?") == "hi"
    assert nlp_parser.detect_language("Will it rain tomorrow in Delhi?") == "en"


def test_location_and_date_extraction_all_cases():
    # 1. "What's the weather in London?" -> London, today (offset 0)
    p1 = nlp_parser.parse("What's the weather in London?")
    assert p1["resolved_location"] == "London"
    assert p1["has_explicit_location"] is True
    assert p1["date_offset"] == 0

    # 2. "Delhi weather tomorrow" -> Delhi, tomorrow (offset 1)
    p2 = nlp_parser.parse("Delhi weather tomorrow")
    assert p2["resolved_location"] == "Delhi"
    assert p2["has_explicit_location"] is True
    assert p2["date_offset"] == 1

    # 3. "Mumbai weather on Sunday" -> Mumbai
    p3 = nlp_parser.parse("Mumbai weather on Sunday")
    assert p3["resolved_location"] == "Mumbai"
    assert p3["has_explicit_location"] is True

    # 4. "15 September weather in Mumbai" -> Mumbai
    p4 = nlp_parser.parse("15 September weather in Mumbai")
    assert p4["resolved_location"] == "Mumbai"
    assert p4["has_explicit_location"] is True

    # 5. "UP ka weather kaisa hai?" -> Uttar Pradesh
    p5 = nlp_parser.parse("UP ka weather kaisa hai?")
    assert p5["resolved_location"] == "Uttar Pradesh"
    assert p5["has_explicit_location"] is True

    # 6. "Punjab mein kal baarish hogi?" -> Punjab, tomorrow (offset 1)
    p6 = nlp_parser.parse("Punjab mein kal baarish hogi?")
    assert p6["resolved_location"] == "Punjab"
    assert p6["has_explicit_location"] is True
    assert p6["date_offset"] == 1

    # 7. "Amritsar ka mausam kaisa hai?" -> Amritsar, today (offset 0)
    p7 = nlp_parser.parse("Amritsar ka mausam kaisa hai?")
    assert p7["resolved_location"] == "Amritsar"
    assert p7["has_explicit_location"] is True
    assert p7["date_offset"] == 0

    # 8. "New York weather tomorrow" -> New York, tomorrow (offset 1)
    p8 = nlp_parser.parse("New York weather tomorrow")
    assert p8["resolved_location"] == "New York"
    assert p8["has_explicit_location"] is True
    assert p8["date_offset"] == 1


def test_intent_extraction():
    parsed = nlp_parser.parse("Kal travel karna safe hai?")
    assert parsed["extracted_intent"] == "travel"

    parsed_agri = nlp_parser.parse("Kal spraying karna suitable hai?")
    assert parsed_agri["extracted_intent"] == "agriculture"

