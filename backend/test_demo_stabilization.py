import requests
import json
import re

BASE_URL = "http://127.0.0.1:8000/api/weather/query"

TEST_QUERIES = [
    {
        "id": 1,
        "name": "Mumbai Today Weather",
        "query": "Mumbai ka mausam kaisa hai aaj",
        "expected_intent": "forecast",
        "expected_loc_contains": "Mumbai",
        "check": lambda r: r.get("weather_facts") is not None and r.get("weather_facts", {}).get("temperature_c") is not None
    },
    {
        "id": 2,
        "name": "Mumbai Tomorrow Weather",
        "query": "Mumbai mein kal mausam kaisa rahega",
        "expected_intent": "forecast",
        "expected_loc_contains": "Mumbai",
        "check": lambda r: "2026-09-09" in r.get("resolved_date", "") or "Tomorrow" in r.get("resolved_date", "")
    },
    {
        "id": 3,
        "name": "Amritsar Today Rain",
        "query": "Amritsar mein aaj barish hogi kya",
        "expected_intent": "rain",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: r.get("weather_facts") is not None and "rain_probability" in r.get("weather_facts", {})
    },
    {
        "id": 4,
        "name": "Amritsar Tomorrow Rain",
        "query": "Amritsar mein kal barish hogi kya",
        "expected_intent": "rain",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: "2026-09-09" in r.get("resolved_date", "") or "Tomorrow" in r.get("resolved_date", "")
    },
    {
        "id": 5,
        "name": "Amritsar Peak Rain Day",
        "query": "Amritsar mein kaun se din sabse zyada baarish hogi",
        "expected_intent": "forecast_peak_day",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: "Amritsar" in r.get("resolved_location", "") and any(w in r.get("grounded_answer", "") for w in ["बारिश", "rain", "पूर्वानुमान", "संभावना", "दिन", "forecast", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    },
    {
        "id": 6,
        "name": "Punjab Regional City Ranking",
        "query": "Punjab mein kal sabse zyada baarish kis city mein hogi",
        "expected_intent": "ranking",
        "expected_loc_contains": "Punjab",
        "check": lambda r: r.get("response_type") == "ranking" and len(r.get("ranking_data", [])) > 0
    },
    {
        "id": 7,
        "name": "Farming Fertilizer Advice",
        "query": "kya main Mumbai mein aaj apne kheton mein khad dal sakta hun",
        "expected_intent": "agriculture_fertilizer",
        "expected_loc_contains": "Mumbai",
        "check": lambda r: any(w in r.get("grounded_answer", "").lower() for w in ["खाद", "fertilizer", "khad", "मौसम", "rain"])
    },
    {
        "id": 8,
        "name": "Farming Spraying Advice",
        "query": "Amritsar mein spray ke liye mausam kaisa hai",
        "expected_intent": "agriculture_spraying",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: any(w in r.get("grounded_answer", "").lower() for w in ["छिड़काव", "spray", "spraying", "हवा", "wind"])
    },
    {
        "id": 9,
        "name": "General Farming Operations",
        "query": "Amritsar mein kheti ke liye mausam kaisa hai",
        "expected_intent": "agriculture",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: any(w in r.get("grounded_answer", "").lower() for w in ["खाद", "छिड़काव", "सिंचाई", "fertilizer", "spraying", "irrigation", "agriculture"])
    },
    {
        "id": 10,
        "name": "Contradiction / Discrepancy Challenge",
        "query": "tumne pahle 10% kaha tha ab 100% bol rahe ho",
        "expected_intent": "contradiction_challenge",
        "expected_loc_contains": "Mumbai",
        "last_location": "Mumbai",
        "check": lambda r: any(w in r.get("grounded_answer", "").lower() for w in ["अपडेट", "डेटा", "आधिकारिक", "update", "model", "verified", "feed", "satellite"])
    },
    {
        "id": 11,
        "name": "Multi-Location Comparison",
        "query": "Mumbai aur Delhi mein kis jagah barish ki sambhavna jyada hai",
        "expected_intent": "comparison",
        "expected_loc_contains": "Mumbai",
        "check": lambda r: r.get("response_type") == "comparison" and len(r.get("comparison_data", [])) == 2
    },
    {
        "id": 12,
        "name": "Multi-Date Activity Comparison",
        "query": "Friday aur Saturday mein kaunsa din bike ride ke liye better hai",
        "expected_intent": "comparison",
        "last_location": "Amritsar",
        "check": lambda r: "Friday" in r.get("resolved_date", "") and "Saturday" in r.get("resolved_date", "")
    },
    {
        "id": 13,
        "name": "Specific Target Date",
        "query": "15 September 2026 ko Amritsar mein barish hogi kya",
        "expected_intent": "rain",
        "expected_loc_contains": "Amritsar",
        "check": lambda r: "2026-09-15" in r.get("resolved_date", "") or "2026-09-15" in r.get("grounded_answer", "")
    },
    {
        "id": 14,
        "name": "Missing Location Clarification",
        "query": "kya aaj barish hogi",
        "expected_intent": "rain",
        "expected_loc_contains": "",
        "check": lambda r: r.get("is_missing_location") is True and r.get("response_type") == "clarification"
    },
    {
        "id": 15,
        "name": "Non-Weather Software Query",
        "query": "Visual Studio code kahan per Milta Hai",
        "expected_intent": "non_weather",
        "expected_loc_contains": "",
        "check": lambda r: r.get("is_non_weather") is True and "vs code" in r.get("grounded_answer", "").lower() or "मौसम" in r.get("grounded_answer", "")
    },
    {
        "id": 16,
        "name": "Bot Identity Query",
        "query": "tumhara naam kya hai",
        "expected_intent": "identity",
        "expected_loc_contains": "",
        "check": lambda r: "WeatherGPT" in r.get("grounded_answer", "")
    },
    {
        "id": 17,
        "name": "Devotional Greeting",
        "query": "jai mata di",
        "expected_intent": "non_weather_greeting",
        "expected_loc_contains": "",
        "check": lambda r: "जय माता दी" in r.get("grounded_answer", "")
    },
    {
        "id": 18,
        "name": "Travel Route Safe Assessment",
        "query": "Delhi se Mumbai bike par travel kar sakta hun aaj?",
        "expected_intent": "bike_ride",
        "expected_loc_contains": "Delhi",
        "check": lambda r: r.get("response_type") == "travel" and r.get("travel_data") is not None
    }
]

def run_tests():
    passed = 0
    failed = 0
    svg_leak_found = 0
    
    print(f"============================================================")
    print(f"RUNNING DEMO STABILIZATION REGRESSION SUITE ({len(TEST_QUERIES)} Tests)")
    print(f"============================================================\n")

    for t in TEST_QUERIES:
        payload = {"query": t["query"]}
        if t.get("last_location"):
            payload["last_location"] = t["last_location"]
            
        try:
            res = requests.post(BASE_URL, json=payload, timeout=25)
            if res.status_code != 200:
                print(f"[FAIL] Test {t['id']}: '{t['name']}' -> HTTP {res.status_code}: {res.text.encode('ascii', 'ignore').decode()}")
                failed += 1
                continue
                
            data = res.json()
            grounded_ans = data.get("grounded_answer", "")
            
            # SVG Leakage Check
            has_svg = bool(re.search(r'<svg[\s\S]*?<\/svg>', grounded_ans, re.I) or 
                           re.search(r'</?svg[^>]*>', grounded_ans, re.I) or 
                           re.search(r'\bsvg\b', grounded_ans, re.I) or 
                           "svgLOW RISKsvg" in grounded_ans or 
                           "svgMax" in grounded_ans)
            if has_svg:
                print(f"[WARN] SVG Leak detected in Test {t['id']}: {grounded_ans[:100]}...")
                svg_leak_found += 1
                
            # Check intent
            actual_intent = data.get("extracted_intent")
            if t.get("expected_intent") and actual_intent != t["expected_intent"]:
                print(f"[FAIL] Test {t['id']}: '{t['name']}' -> Expected intent '{t['expected_intent']}', got '{actual_intent}'")
                failed += 1
                continue
                
            # Check location
            actual_loc = data.get("resolved_location", "")
            if t.get("expected_loc_contains") and t["expected_loc_contains"].lower() not in actual_loc.lower():
                print(f"[FAIL] Test {t['id']}: '{t['name']}' -> Expected location containing '{t['expected_loc_contains']}', got '{actual_loc.encode('ascii', 'ignore').decode()}'")
                failed += 1
                continue
                
            # Custom assertions
            if not t["check"](data):
                print(f"[FAIL] Test {t['id']}: '{t['name']}' -> Custom check assertion failed! Ans: {grounded_ans[:120].encode('ascii', 'ignore').decode()}")
                failed += 1
                continue
                
            print(f"[PASS] Test {t['id']:02d}: '{t['name']}' (Intent: {actual_intent}, Loc: '{actual_loc.encode('ascii', 'ignore').decode()}')")
            passed += 1
            
        except Exception as e:
            print(f"[ERROR] Test {t['id']}: '{t['name']}' -> Exception: {e}")
            failed += 1

    print(f"\n============================================================")
    print(f"RESULTS: {passed}/{len(TEST_QUERIES)} PASSED | {failed} FAILED | {svg_leak_found} SVG LEAKS")
    print(f"============================================================")
    assert failed == 0, f"{failed} test(s) failed!"
    assert svg_leak_found == 0, f"{svg_leak_found} SVG leak(s) found!"

if __name__ == "__main__":
    run_tests()
