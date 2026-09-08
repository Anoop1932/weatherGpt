import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8')
base_url = 'http://127.0.0.1:8000/api/weather/query'

queries = [
    # A)
    {
        "id": "A",
        "query": "cal Lucknow mein tapman",
        "expected_loc": "Lucknow",
        "expected_type": "weather",
        "check": lambda d: "lucknow" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather"
    },
    # B)
    {
        "id": "B",
        "query": "cal Lucknow ka vedar batao",
        "expected_loc": "Lucknow",
        "expected_type": "weather",
        "check": lambda d: "lucknow" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather"
    },
    # C)
    {
        "id": "C",
        "query": "cal Lucknow ka vedar kaisa rahega",
        "expected_loc": "Lucknow",
        "expected_type": "weather",
        "check": lambda d: "lucknow" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather"
    },
    # D)
    {
        "id": "D",
        "query": "cal Amritsar ka mausam batao",
        "expected_loc": "Amritsar",
        "expected_type": "weather",
        "check": lambda d: "amritsar" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather"
    },
    # E)
    {
        "id": "E",
        "query": "Amritsar Ka vedar Kaisa Rahega cal",
        "expected_loc": "Amritsar",
        "expected_type": "weather",
        "check": lambda d: "amritsar" in d.get("resolved_location", "").lower() and d.get("detected_language") in ["hi", "en"]
    },
    # F)
    {
        "id": "F",
        "query": "Hisar Haryana mein abhi vartman ka tapman kya hai",
        "expected_loc": "Hisar",
        "expected_type": "weather",
        "check": lambda d: "hisar" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather" and "वर्तमान तापमान" in d.get("grounded_answer", "")
    },
    # G)
    {
        "id": "G",
        "query": "is it good to go for bike ride in Mumbai tomorrow",
        "expected_loc": "Mumbai",
        "expected_type": "weather",
        "check": lambda d: "mumbai" in d.get("resolved_location", "").lower() and d.get("response_type") == "weather" and not d.get("is_missing_location")
    },
    # H)
    {
        "id": "H1",
        "query": "kya hal hai",
        "expected_loc": "",
        "expected_type": "conversation",
        "check": lambda d: d.get("response_type") == "conversation" and d.get("is_non_weather") and not d.get("weather_facts")
    },
    {
        "id": "H2",
        "query": "kya haal hai bhai",
        "expected_loc": "",
        "expected_type": "conversation",
        "check": lambda d: d.get("response_type") == "conversation" and d.get("is_non_weather")
    },
    {
        "id": "H3",
        "query": "how are you",
        "expected_loc": "",
        "expected_type": "conversation",
        "check": lambda d: d.get("response_type") == "conversation" and d.get("is_non_weather")
    },
    # I)
    {
        "id": "I",
        "query": "Amritsar Mein Barish kab Hogi",
        "expected_loc": "Amritsar",
        "expected_type": "weather",
        "check": lambda d: "amritsar" in d.get("resolved_location", "").lower() and any(w in d.get("grounded_answer", "") for w in ["पूर्वानुमान", "संभावना", "बारिश", "forecast", "rain", "hour"])
    },
    # J)
    {
        "id": "J",
        "query": "Amritsar aur London Mein tapman Kitna kitna hai compare karo",
        "expected_loc": "Amritsar vs London",
        "expected_type": "comparison",
        "check": lambda d: d.get("response_type") == "comparison" and d.get("comparison_data") and len(d.get("comparison_data")) >= 2
    },
    # K)
    {
        "id": "K",
        "query": "India mein sabse Jyada Barish kahan hogi",
        "expected_loc": "India",
        "expected_type": "ranking",
        "check": lambda d: d.get("response_type") == "ranking" and d.get("ranking_data") and len(d.get("ranking_data")) >= 2
    },
    # L)
    {
        "id": "L",
        "query": "India mein sabse Jyada Barish kaun si jagah per Hogi",
        "expected_loc": "India",
        "expected_type": "ranking",
        "check": lambda d: d.get("response_type") == "ranking" and d.get("ranking_data") and len(d.get("ranking_data")) >= 2
    }
]

print("=" * 80)
print("RUNNING WEATHERGPT FINAL AUDIT VERIFICATION SUITE")
print("=" * 80)

passed = 0
failed = 0

for t in queries:
    qid = t["id"]
    q = t["query"]
    try:
        r = httpx.post(base_url, json={"query": q, "location": "Amritsar"}, timeout=20.0)
        d = r.json()
        ok = t["check"](d)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"[{status}] Test {qid}: '{q}'")
        print(f"   -> Response Type: {d.get('response_type')} | Location: {d.get('resolved_location')} | Lang: {d.get('detected_language')}")
        ans_preview = d.get('grounded_answer', '').replace('\n', ' ')[:100]
        print(f"   -> Answer: {ans_preview}...")
        if not ok:
            print(f"   -> RAW RESPONSE: {d}")
    except Exception as e:
        failed += 1
        print(f"[FAIL] Test {qid}: '{q}' -> Exception: {e}")

print("=" * 80)
print(f"FINAL AUDIT RESULTS: TOTAL={len(queries)} | PASSED={passed} | FAILED={failed}")
print("=" * 80)
