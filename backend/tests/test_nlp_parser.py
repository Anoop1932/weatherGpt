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


def test_section_aa_test_matrix():
    # 1. Non-weather Conversation must not trigger weather
    p_conv1 = nlp_parser.parse("kya hal hai")
    assert p_conv1["intent_category"] == "CONVERSATION"
    assert p_conv1["resolved_location"] == ""

    p_conv2 = nlp_parser.parse("kya haal hai bhai")
    assert p_conv2["intent_category"] == "CONVERSATION"

    p_conv3 = nlp_parser.parse("how are you")
    assert p_conv3["intent_category"] == "CONVERSATION"

    p_conv4 = nlp_parser.parse("tum kaise ho")
    assert p_conv4["intent_category"] == "CONVERSATION"

    # 2. Cycling / Bike Ride extraction
    p_bike = nlp_parser.parse("is it good to go for bike ride in Mumbai tomorrow")
    assert p_bike["intent_category"] in ["BIKE_RIDE", "CYCLING", "CYCLING/BIKE_RIDE"]
    assert p_bike["extracted_intent"] in ["cycling", "bike_ride", "bike ride"]
    assert p_bike["resolved_location"] == "Mumbai"
    assert p_bike["date_offset"] == 1

    # 3. Current Weather (vartman / abhi)
    p_curr = nlp_parser.parse("Hisar Haryana mein abhi vartman ka tapman kya hai")
    assert p_curr["resolved_location"] == "Hisar, Haryana"
    assert p_curr["date_offset"] == 0
    assert p_curr["is_current"] is True

    # 4. Outdoor events
    p_events = nlp_parser.parse("Is tomorrow good for outdoor events in Patna, Bihar, India?")
    assert p_events["intent_category"] == "OUTDOOR_EVENT"
    assert "Patna" in p_events["resolved_location"]
    assert p_events["date_offset"] == 1

    # 5. Comparison
    p_comp = nlp_parser.parse("Delhi aur Mumbai ka weather compare karo")
    assert p_comp["intent_category"] == "COMPARISON"
    assert p_comp["comparison_locations"] == ["Delhi", "Mumbai"]

    # 6. Multi-date comparison
    p_date_comp = nlp_parser.parse("Friday aur Saturday mein kaunsa din bike ride ke liye better hai?")
    assert p_date_comp["intent_category"] == "COMPARISON"
    assert "Friday" in p_date_comp["comparison_dates"]
    assert "Saturday" in p_date_comp["comparison_dates"]

    # 7. Historical Weather
    p_hist1 = nlp_parser.parse("kal Patna mein temperature kya tha?")
    assert p_hist1["intent_category"] == "HISTORICAL_WEATHER"
    assert p_hist1["is_historical"] is True
    assert p_hist1["date_offset"] == -1
    assert p_hist1["resolved_location"] == "Patna"

    p_hist2 = nlp_parser.parse("yesterday Mumbai mein rain hui?")
    assert p_hist2["intent_category"] == "HISTORICAL_WEATHER"
    assert p_hist2["is_historical"] is True
    assert p_hist2["date_offset"] == -1
    assert p_hist2["resolved_location"] == "Mumbai"

    # 8. Follow-up Context Preservation
    p_fu1 = nlp_parser.parse("kal?", last_location="Patna", last_date="2026-09-08")
    assert p_fu1["resolved_location"] == "Patna"
    assert p_fu1["date_offset"] == 1

    p_fu2 = nlp_parser.parse("barish?", last_location="Patna", last_date="2026-09-09")
    assert p_fu2["resolved_location"] == "Patna"
    assert p_fu2["extracted_intent"] == "rain"

    p_fu3 = nlp_parser.parse("bike ride ke liye?", last_location="Patna", last_date="2026-09-09")
    assert p_fu3["resolved_location"] == "Patna"
    assert p_fu3["intent_category"] in ["BIKE_RIDE", "CYCLING", "CYCLING/BIKE_RIDE"]

    # 9. Explicit location overrides previous context
    p_override = nlp_parser.parse("Delhi mein kal barish hogi?", last_location="Patna")
    assert p_override["resolved_location"] == "Delhi"
    assert p_override["has_explicit_location"] is True

