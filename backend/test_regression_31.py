import asyncio
import re
import sys
import httpx
from app.main import app

sys.stdout.reconfigure(encoding='utf-8')

TEST_MATRIX = [
    # 1. Amritsar rain
    {
        "query": "Amritsar Mein Barish Hogi",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 2. cal Bihar Patna
    {
        "query": "cal Bihar Patna mein Barish Hogi Ki Nahin",
        "expected_type": "weather",
        "expected_loc": "Patna",
        "should_have_weather_facts": True
    },
    # 3. Punjab ranking
    {
        "query": "Punjab Mein Barish kahan per Hogi batao",
        "expected_type": "ranking",
        "expected_loc": "Punjab",
        "should_have_weather_facts": True
    },
    # 4. Punjab ke kis state
    {
        "query": "Punjab ke kis state mein sabse Jyada barish ho rahi hai",
        "expected_type": "ranking",
        "expected_loc": "Punjab",
        "should_have_weather_facts": True
    },
    # 5. India sabse jyada barish
    {
        "query": "India mein sabse Jyada Barish kahan per ho rahi hai is time",
        "expected_type": "ranking",
        "expected_loc": "India",
        "should_have_weather_facts": True
    },
    # 6. Mumbai vedar aaj ka
    {
        "query": "Mumbai ka vedar kya hai aaj ka",
        "expected_type": "weather",
        "expected_loc": "Mumbai",
        "should_have_weather_facts": True
    },
    # 7. Mumbai umbrella
    {
        "query": "Should I carry an umbrella today in Mumbai, Maharashtra, India?",
        "expected_type": "weather",
        "expected_loc": "Mumbai",
        "should_have_weather_facts": True
    },
    # 8. Capabilities
    {
        "query": "Tumhen Kya Aata Hai",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True
    },
    # 9. Identity
    {
        "query": "tumhara naam kya hai",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True,
        "content_check": "WeatherGPT"
    },
    # 10. Devotional greeting
    {
        "query": "jai mata di",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True,
        "content_check": "जय माता दी"
    },
    # 11. Conversational banter 1
    {
        "query": "kya hal hai",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True
    },
    # 12. Conversational banter 2
    {
        "query": "kya haal hai bhai",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True
    },
    # 13. chhajje Amritsar
    {
        "query": "chhajje Amritsar se Barish Hogi Ki Nahin",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 14. Aaj Amritsar
    {
        "query": "Aaj Amritsar se Barish Hogi",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 15. Amritsar agriculture spraying
    {
        "query": "Is farming spraying suitable tomorrow in Amritsar, Punjab, India?",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 16. Missing location umbrella
    {
        "query": "kya Ham amrela Lekar nikal sakte hain Bahar",
        "expected_type": "clarification",
        "should_have_weather_facts": False,
        "is_missing_location": True
    },
    # 17. Explicit location umbrella
    {
        "query": "kya Ham Amritsar Mein ambrella Lekar nikal sakte hain Bahar",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 18. Incomplete umbrella query
    {
        "query": "umbrella is",
        "expected_type": "clarification",
        "should_have_weather_facts": False,
        "is_non_weather": True
    },
    # 19. Non-weather VS Code
    {
        "query": "Visual Studio code kahan per Milta Hai",
        "expected_type": "conversation",
        "should_have_weather_facts": False,
        "is_non_weather": True,
        "content_check": "VS Code"
    },
    # 20. Locality Nangli Amritsar
    {
        "query": "Amritsar ki Nangli Mein Barish Hai Ki Nahin",
        "expected_type": "weather",
        "expected_loc": "Nangli",
        "should_have_weather_facts": True,
        "content_check": "Nangli"
    },
    # 21. Live rain happening
    {
        "query": "is rain is happening in Amritsar",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 22. Unclear query fragment
    {
        "query": "is which form in Amritsar",
        "expected_type": "clarification",
        "should_have_weather_facts": False,
        "is_non_weather": True
    },
    # 23. Sunday weather
    {
        "query": "Sunday weather of Amritsar",
        "expected_type": "weather",
        "expected_loc": "Amritsar",
        "should_have_weather_facts": True
    },
    # 24. Barcelona vedar
    {
        "query": "Barcelona ka vedar batao",
        "expected_type": "weather",
        "expected_loc": "Barcelona",
        "should_have_weather_facts": True
    },
    # 25. Barcelona spraying tomorrow
    {
        "query": "Is farming spraying suitable tomorrow in Barcelona, Catalonia, Spain?",
        "expected_type": "weather",
        "expected_loc": "Barcelona",
        "should_have_weather_facts": True
    },
    # 26. Barcelona outdoor events tomorrow
    {
        "query": "Is tomorrow good for outdoor events in Barcelona, Catalonia, Spain?",
        "expected_type": "weather",
        "expected_loc": "Barcelona",
        "should_have_weather_facts": True
    },
    # 27. Barcelona umbrella
    {
        "query": "kya hum Barcelona mein umbrella lekar bahar ja sakte hain?",
        "expected_type": "weather",
        "expected_loc": "Barcelona",
        "should_have_weather_facts": True
    },
    # 28. Guwahati Assam
    {
        "query": "Guwahati Assam ka weather aaj kaisa hai?",
        "expected_type": "weather",
        "expected_loc": "Guwahati",
        "should_have_weather_facts": True
    },
    # 29. Lucknow tomorrow
    {
        "query": "Kal Lucknow ka weather kaisa rahega?",
        "expected_type": "weather",
        "expected_loc": "Lucknow",
        "should_have_weather_facts": True
    },
    # 30. London tomorrow
    {
        "query": "London weather tomorrow",
        "expected_type": "weather",
        "expected_loc": "London",
        "should_have_weather_facts": True
    },
    # 31. Comparison Amritsar and London
    {
        "query": "Compare Amritsar and London temperature",
        "expected_type": "comparison",
        "should_have_weather_facts": True
    }
]

async def run_regression():
    passed = 0
    total = len(TEST_MATRIX)
    print("=" * 70)
    print(f"WEATHERGPT — PART 26 REGRESSION TEST MATRIX ({total} QUERIES)")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        for idx, tc in enumerate(TEST_MATRIX, 1):
            q = tc["query"]
            http_resp = await client.post("/api/weather/query", json={"query": q})
            data = http_resp.json()

            errors = []

            resp_type = data.get("response_type")
            res_loc = data.get("resolved_location") or ""
            wf = data.get("weather_facts")
            is_non = data.get("is_non_weather")
            is_miss = data.get("is_missing_location")
            ans = data.get("grounded_answer") or ""

            # 1. Check response_type
            if tc.get("expected_type") and resp_type != tc["expected_type"] and not (tc["expected_type"] == "weather" and resp_type == "activity"):
                errors.append(f"Expected response_type '{tc['expected_type']}', got '{resp_type}'")

            # 2. Check resolved_location
            if tc.get("expected_loc") and tc["expected_loc"].lower() not in res_loc.lower():
                errors.append(f"Expected location to contain '{tc['expected_loc']}', got '{res_loc}'")

            # 3. Check weather_facts presence/absence
            if tc.get("should_have_weather_facts") is False and wf is not None:
                errors.append(f"Expected weather_facts to be None for non-weather query, but got data")

            # 4. Check is_non_weather
            if tc.get("is_non_weather") is True and not is_non:
                errors.append(f"Expected is_non_weather to be True")

            # 5. Check is_missing_location
            if tc.get("is_missing_location") is True and not is_miss:
                errors.append(f"Expected is_missing_location to be True")

            # 6. Check content keyword
            if tc.get("content_check") and tc["content_check"].lower() not in ans.lower():
                errors.append(f"Expected answer to contain '{tc['content_check']}'")

            # 7. CRITICAL: SVG Leakage Check
            if re.search(r'<svg|<\/svg>|\bsvg\b|svgLOW|svgMax', ans, re.IGNORECASE):
                errors.append("CRITICAL: Raw SVG string leaked into response text!")

            status = "PASS" if not errors else "FAIL"
            if status == "PASS":
                passed += 1
                print(f"[{idx:02d}/31] PASS: '{q}' -> type={resp_type}, loc='{res_loc}'")
            else:
                print(f"[{idx:02d}/31] FAIL: '{q}'")
                for err in errors:
                    print(f"       -> {err}")
                print(f"       Answer preview: {ans[:120]}...")

    print("=" * 70)
    print(f"REGRESSION MATRIX RESULTS: {passed}/{total} PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 70)
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_regression())
    sys.exit(0 if success else 1)
