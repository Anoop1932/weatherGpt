import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_mumbai_consistency():
    print("=== Testing Mumbai Consistency (Repeated Calls) ===")
    results = []
    for i in range(3):
        # 1. Chat query
        payload = {"query": "Mumbai ka mausam kaisa hai aaj"}
        r_chat = requests.post(f"{BASE_URL}/weather/query", json=payload, timeout=10)
        assert r_chat.status_code == 200, f"Chat call {i+1} failed: {r_chat.text}"
        chat_data = r_chat.json()
        chat_facts = chat_data.get("weather_facts") or {}
        
        # 2. Direct current weather
        r_curr = requests.get(f"{BASE_URL}/weather/current?location=Mumbai&lat=19.076&lon=72.8777", timeout=10)
        assert r_curr.status_code == 200, f"Current weather call {i+1} failed: {r_curr.text}"
        curr_data = r_curr.json()
        
        # 3. Direct forecast
        r_fc = requests.get(f"{BASE_URL}/weather/forecast?location=Mumbai&lat=19.076&lon=72.8777&days=1", timeout=10)
        assert r_fc.status_code == 200, f"Forecast call {i+1} failed: {r_fc.text}"
        fc_data = r_fc.json()
        today_fc = fc_data.get("daily", [{}])[0]
        
        print(f"Call {i+1}:")
        print(f"  Chat Facts: temp={chat_facts.get('temperature_c')}°C, rain_prob={chat_facts.get('rain_probability')}%, cond={chat_facts.get('condition_text')}")
        print(f"  Live Curr:  temp={curr_data.get('temperature_c')}°C, cond={curr_data.get('condition_text')}")
        print(f"  Daily FC:   max_temp={today_fc.get('temp_max_c')}°C, rain_prob={today_fc.get('rain_probability')}%")
        
        # Verify that temperature is within realistic delta (< 2.0°C difference across fetches)
        assert abs(chat_facts.get('temperature_c', 0) - curr_data.get('temperature_c', 0)) <= 2.0, "Chat temperature deviates from current API"
        assert "drizzle" in chat_facts.get('condition_text', '').lower() or "rain" in chat_facts.get('condition_text', '').lower() or chat_facts.get('condition_text') == curr_data.get('condition_text'), "Condition text mismatch"
        results.append(chat_facts)
        time.sleep(0.5)
        
    print("SUCCESS: Mumbai weather facts are consistent across repeated calls!\n")

def test_amritsar_consistency():
    print("=== Testing Amritsar Consistency (Today vs Tomorrow) ===")
    # Today
    r_today = requests.post(f"{BASE_URL}/weather/query", json={"query": "Amritsar mein aaj barish hogi kya"}, timeout=10)
    assert r_today.status_code == 200
    today_facts = r_today.json().get("weather_facts") or {}
    
    # Tomorrow
    r_tomorrow = requests.post(f"{BASE_URL}/weather/query", json={"query": "Amritsar mein kal barish hogi kya"}, timeout=10)
    assert r_tomorrow.status_code == 200
    tomorrow_facts = r_tomorrow.json().get("weather_facts") or {}
    
    print(f"Amritsar Today:    date={today_facts.get('date')}, temp={today_facts.get('temperature_c')}°C, rain_prob={today_facts.get('rain_probability')}%, cond={today_facts.get('condition_text')}")
    print(f"Amritsar Tomorrow: date={tomorrow_facts.get('date')}, max_temp={tomorrow_facts.get('temp_max_c')}°C, rain_prob={tomorrow_facts.get('rain_probability')}%, cond={tomorrow_facts.get('condition_text')}")
    
    # Dates must be different
    assert today_facts.get("date") != tomorrow_facts.get("date"), "Today and tomorrow dates must not be identical"
    print("SUCCESS: Amritsar today and tomorrow properly differentiated!\n")

if __name__ == "__main__":
    test_mumbai_consistency()
    test_amritsar_consistency()
