import requests
import json
import re
import sys

BASE_URL = "http://127.0.0.1:8000/api/weather/query"

FORBIDDEN_LEAKED_LOCS = [
    "carry, haiti",
    "start, louisiana",
    "cities services",
    "apnenik",
    "bostanju",
    "bachanahalli"
]

def check_svg_leak(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r'<svg[\s\S]*?</svg>',
        r'<svg',
        r'</svg>',
        r'\bsvg\b',
        r'svgLOW',
        r'svgMax',
        r'svgRain',
        r'svgWind',
        r'svgCond'
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False

def check_html_leak(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r'<[a-z][\s\S]*?>', text, re.IGNORECASE))

def run_tests():
    total_tests = 0
    passed_tests = 0
    failed_details = []

    print("=" * 70)
    print("STARTING WEATHERGPT 48-POINT FINAL REGRESSION SUITE")
    print("=" * 70)

    # Helper to call API
    def call_api(query, context=None):
        payload = {
            "query": query,
            "location": "Amritsar",
            "language": "en"
        }
        if context:
            payload.update(context)
        resp = requests.post(BASE_URL, json=payload, timeout=30)
        return resp.status_code, resp.json()

    # SECTION 1: CONVERSATION
    conv_queries = [
        "tumhara naam kya hai",
        "kya haal hai",
        "kya haal hai bhai",
        "jai mata di",
        "tum kya kya kar sakte ho?",
        "Visual Studio Code kahan milta hai?"
    ]
    for q in conv_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        wf = data.get("weather_facts")
        rl = data.get("risk_level")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != "conversation":
            errs.append(f"response_type was '{rtype}', expected 'conversation'")
        if wf is not None:
            errs.append("weather_facts was not null (stale weather card!)")
        if rl is not None:
            errs.append("risk_level was not null")
        if check_svg_leak(ans):
            errs.append("SVG leaked into grounded_answer")
        if check_html_leak(ans):
            errs.append("HTML leaked into grounded_answer")
        
        if not errs:
            passed_tests += 1
            print(f"[PASS] CONV: '{q}' -> {rtype}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] CONV: '{q}' -> {', '.join(errs)}")

    # SECTION 2: LOCATION DISAMBIGUATION & NORMALIZATION
    loc_queries = [
        ("Nepal ka weather dikhao", ["Nepal"], ["Uttar Pradesh", "India"]),
        ("Dubai ka weather dikhao", ["Dubai", "United Arab Emirates"], ["Uttar Pradesh", "India"]),
        ("Arunachal Pradesh ka weather dikhao", ["Arunachal Pradesh"], ["Arunachalapuram"]),
        ("Asam ka weather dikhao", ["Assam"], []),
        ("Guwahati Asam ka weather dikhao", ["Guwahati", "Assam"], [])
    ]
    for q, expected_keywords, forbidden_keywords in loc_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")
        wf = data.get("weather_facts")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != "weather":
            errs.append(f"response_type was '{rtype}', expected 'weather'")
        if not wf:
            errs.append("missing weather_facts")
        for kw in expected_keywords:
            if kw.lower() not in loc.lower() and kw.lower() not in ans.lower():
                errs.append(f"missing expected keyword '{kw}' in location ('{loc}')")
        for fkw in forbidden_keywords:
            if fkw.lower() in loc.lower():
                errs.append(f"forbidden keyword '{fkw}' found in location ('{loc}')")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] LOC: '{q}' -> {loc}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] LOC: '{q}' -> {', '.join(errs)}")

    # SECTION 3: CURRENT WEATHER
    curr_queries = [
        "is rain happening in Amritsar",
        "Amritsar mein abhi barish ho rahi hai?"
    ]
    for q in curr_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")
        wf = data.get("weather_facts") or {}

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if "amritsar" not in loc.lower():
            errs.append(f"location was '{loc}', expected Amritsar")
        if not wf.get("is_current_observation"):
            errs.append("is_current_observation was not True")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] CURRENT: '{q}' -> is_curr={wf.get('is_current_observation')}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] CURRENT: '{q}' -> {', '.join(errs)}")

    # SECTION 4: FORECAST
    fc_queries = [
        ("Kal Amritsar mein barish hogi?", 1),
        ("Sunday weather of Amritsar", None)
    ]
    for q, min_offset in fc_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")
        wf = data.get("weather_facts") or {}

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if "amritsar" not in loc.lower():
            errs.append(f"location was '{loc}', expected Amritsar")
        if wf.get("is_current_observation"):
            errs.append("forecast query marked as is_current_observation")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] FORECAST: '{q}' -> {data.get('resolved_date')}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] FORECAST: '{q}' -> {', '.join(errs)}")

    # SECTION 5: ACTIVITY SUITABILITY
    act_queries = [
        ("Should I carry an umbrella", None, "clarification", False), # No loc given without context -> clarification
        ("Should I carry an umbrella in Mumbai?", "Mumbai", "activity", True),
        ("kya main Mumbai mein chhata lekar bahar ja sakta hun?", "Mumbai", "activity", True),
        ("kya main Mumbai mein bike se travel kar sakta hun?", "Mumbai", "activity", True),
        ("kya Mumbai mein farming suitable hai?", "Mumbai", "activity", True),
        ("Is farming spraying suitable tomorrow in Barcelona, Catalonia, Spain?", "Barcelona", "activity", True),
        ("Is tomorrow good for outdoor events in Barcelona, Catalonia, Spain?", "Barcelona", "activity", True)
    ]
    for q, expected_loc, expected_rtype, expect_facts in act_queries:
        total_tests += 1
        # Call without context for first one
        ctx = None if expected_loc is None else {"location": expected_loc}
        status, data = call_api(q, context=ctx)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != expected_rtype:
            errs.append(f"response_type was '{rtype}', expected '{expected_rtype}'")
        if expected_loc and expected_loc.lower() not in loc.lower():
            errs.append(f"location '{loc}' does not contain expected '{expected_loc}'")
        for fl in FORBIDDEN_LEAKED_LOCS:
            if fl in loc.lower():
                errs.append(f"geocoding leak: '{fl}' in location '{loc}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] ACTIVITY: '{q}' -> {rtype} ({loc})")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] ACTIVITY: '{q}' -> {', '.join(errs)}")

    # SECTION 6: FARMING / KHAD QUERIES
    farm_queries = [
        ("Kya main apne kheton mein khad daal sakta hun, aaj barish hogi?", "clarification", None),
        ("kya main Mumbai mein aaj kheton mein kaam kar sakta hun", "activity", "Mumbai"),
        ("Is farming is allowed in Maharashtra for today", "clarification", "Maharashtra"),
        ("cal Guwahati Assam mein farming aur spraying ke liye suitable weather hai", "activity", "Guwahati")
    ]
    for q, expected_rtype, expected_loc in farm_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != expected_rtype:
            errs.append(f"response_type was '{rtype}', expected '{expected_rtype}'")
        if expected_loc and expected_loc.lower() not in loc.lower() and expected_loc.lower() not in ans.lower():
            errs.append(f"expected '{expected_loc}' in location/answer")
        for fl in FORBIDDEN_LEAKED_LOCS:
            if fl in loc.lower():
                errs.append(f"geocoding leak: '{fl}' in location '{loc}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] FARMING: '{q}' -> {rtype} ({loc or 'clarification'})")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] FARMING: '{q}' -> {', '.join(errs)}")

    # SECTION 7: REGIONAL QUERIES & RANKING
    reg_queries = [
        ("Punjab mein kal sabse zyada baarish kis city mein hogi?", "ranking", "Punjab"),
        ("Punjab ke kaun se cities mein barish hogi?", "ranking", "Punjab"),
        ("India mein sabse jyada barish kahan ho rahi hai?", "ranking", "India"),
        ("India ke shahron ko compare karo", "clarification", "India"),
        ("India ke sabhi shahron ka comparison karo weather ke hisab se", "clarification", "India")
    ]
    for q, expected_rtype, expected_region in reg_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != expected_rtype:
            errs.append(f"response_type was '{rtype}', expected '{expected_rtype}'")
        if expected_rtype == "ranking" and not data.get("ranking_data"):
            errs.append("missing ranking_data in ranking response")
        # Ensure 'cities' or 'shahron' was NOT geocoded
        if "cities" in loc.lower() or "shahron" in loc.lower():
            errs.append(f"false geocoding of cities/shahron: '{loc}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] REGIONAL: '{q}' -> {rtype}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] REGIONAL: '{q}' -> {', '.join(errs)}")

    # SECTION 8: MULTI-CITY COMPARISON
    comp_queries = [
        ("Amritsar aur Delhi compare karo", ["Amritsar", "Delhi"]),
        ("Mumbai aur Amritsar ka weather compare karo", ["Mumbai", "Amritsar"]),
        ("India aur Dubai ka temperature compare karo", ["India", "Dubai"]),
        ("Mumbai aur Delhi mein kis jagah barish ki sambhavna jyada hai", ["Mumbai", "Delhi"])
    ]
    for q, expected_pair in comp_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        cdata = data.get("comparison_data") or []

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != "comparison":
            errs.append(f"response_type was '{rtype}', expected 'comparison'")
        if len(cdata) < 2:
            errs.append(f"comparison_data count {len(cdata)} < 2")
        loc_names = " ".join([c.get("location", "") for c in cdata]).lower()
        for ep in expected_pair:
            if ep.lower() not in loc_names and ep.lower() not in ans.lower():
                errs.append(f"missing expected city '{ep}' in comparison data/answer")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] COMPARISON: '{q}' -> {rtype} ({[c.get('location') for c in cdata]})")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] COMPARISON: '{q}' -> {', '.join(errs)}")

    # SECTION 9: TRAVEL ROUTE QUERIES
    travel_queries = [
        ("Delhi se Mumbai bike par travel kar sakta hun aaj?", "Delhi", "Mumbai"),
        ("Kal Amritsar se Jalandhar bike se jaana safe rahega?", "Amritsar", "Jalandhar")
    ]
    for q, exp_origin, exp_dest in travel_queries:
        total_tests += 1
        status, data = call_api(q)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        tdata = data.get("travel_data") or {}

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != "travel":
            errs.append(f"response_type was '{rtype}', expected 'travel'")
        if not tdata.get("origin") or not tdata.get("destination"):
            errs.append("missing origin or destination in travel_data")
        orig_name = tdata.get("origin", {}).get("location", "")
        dest_name = tdata.get("destination", {}).get("location", "")
        if exp_origin.lower() not in orig_name.lower():
            errs.append(f"expected origin '{exp_origin}', got '{orig_name}'")
        if exp_dest.lower() not in dest_name.lower():
            errs.append(f"expected destination '{exp_dest}', got '{dest_name}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] TRAVEL: '{q}' -> {orig_name} -> {dest_name}")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] TRAVEL: '{q}' -> {', '.join(errs)}")

    # SECTION 10: CONVERSATIONAL FOLLOW-UP DIALOGUE CHAIN
    print("\n--- Testing Conversational Context Chain ---")
    dialogue_chain = [
        # Turn 1: Initial query
        ("Amritsar ka weather batao", {}, "weather", "Amritsar"),
        # Turn 2: What if I go on Sunday? (Reuses Amritsar, updates date)
        ("What if I go on Sunday?", {"last_location": "Amritsar", "last_intent": "weather"}, "weather", "Amritsar"),
        # Turn 3: Compare it with Delhi. (Should compare Amritsar with Delhi)
        ("Compare it with Delhi.", {"last_location": "Amritsar", "last_locations": ["Amritsar"], "last_intent": "weather"}, "comparison", "Amritsar"),
        # Turn 4: Should I carry an umbrella? (Should use Amritsar or Delhi, not Carry, Haiti)
        ("Should I carry an umbrella?", {"last_location": "Amritsar", "last_locations": ["Amritsar", "Delhi"], "last_intent": "comparison"}, "activity", "Amritsar"),
        # Turn 5: What about rain? (Follow-up metric)
        ("What about rain?", {"last_location": "Amritsar", "last_intent": "activity"}, "weather", "Amritsar"),
        # Turn 6: What about temperature? (Follow-up metric)
        ("What about temperature?", {"last_location": "Amritsar", "last_intent": "weather"}, "weather", "Amritsar"),
        # Turn 7: What about farming? (Follow-up activity)
        ("What about farming?", {"last_location": "Amritsar", "last_intent": "weather"}, "activity", "Amritsar")
    ]
    for q, ctx, expected_rtype, exp_loc in dialogue_chain:
        total_tests += 1
        status, data = call_api(q, context=ctx)
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        if rtype != expected_rtype:
            errs.append(f"response_type was '{rtype}', expected '{expected_rtype}'")
        for fl in FORBIDDEN_LEAKED_LOCS:
            if fl in loc.lower():
                errs.append(f"false geocoding: '{fl}' in '{loc}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] FOLLOW-UP: '{q}' -> {rtype} (loc={loc or 'comparison'})")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] FOLLOW-UP: '{q}' -> {', '.join(errs)}")

    # SECTION 11: RAIN TIMING & OUTDOOR TIMING
    timing_queries = [
        ("rain kab start hone ki possibility hai", "Mumbai"),
        ("barish kab start hogi?", "Mumbai"),
        ("when will it rain?", "Mumbai"),
        ("Mujhe barish se bachna hai aur mujhe bahar bhi jana hai to badhiya time kaun sa hai", "Mumbai")
    ]
    for q, ctx_loc in timing_queries:
        total_tests += 1
        # Pass location context so it resolves timing on context location without false geocoding
        status, data = call_api(q, context={"last_location": ctx_loc, "location": ctx_loc})
        ans = data.get("grounded_answer", "")
        rtype = data.get("response_type", "")
        loc = data.get("resolved_location", "")

        errs = []
        if status != 200:
            errs.append(f"HTTP status {status}")
        for fl in FORBIDDEN_LEAKED_LOCS:
            if fl in loc.lower():
                errs.append(f"false geocoding: '{fl}' in '{loc}'")
        if "start" in loc.lower() or "bachna" in loc.lower() or "badhiya" in loc.lower():
            errs.append(f"false geocoding of timing words: '{loc}'")
        if check_svg_leak(ans):
            errs.append("SVG leaked")

        if not errs:
            passed_tests += 1
            print(f"[PASS] TIMING: '{q}' -> {rtype} (loc={loc})")
        else:
            failed_details.append((q, errs))
            print(f"[FAIL] TIMING: '{q}' -> {', '.join(errs)}")

    print("=" * 70)
    print(f"RESULTS: {passed_tests}/{total_tests} TESTS PASSED ({passed_tests/total_tests*100:.1f}%)")
    print("=" * 70)
    if failed_details:
        print("\nFAILURES:")
        for q, errs in failed_details:
            print(f"- '{q}': {errs}")
        sys.exit(1)
    else:
        print("ALL 48 REGRESSION CHECKS PASSED PERFECTLY!")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()
