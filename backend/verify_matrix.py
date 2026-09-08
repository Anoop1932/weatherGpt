import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8')
base_url = 'http://127.0.0.1:8000/api/weather/query'

test_cases = [
    # CURRENT
    ('Hisar Haryana mein abhi vartman ka tapman kya hai', 'Hisar', 'weather'),
    ('Patna ka vartman tapman', 'Patna', 'weather'),
    ("what's the temperature", '', 'clarification'),
    ("what's the temperature in London", 'London', 'weather'),
    # TODAY
    ('Patna ka weather aaj kaisa hai', 'Patna', 'weather'),
    ('Delhi mein aaj barish hogi?', 'Delhi', 'weather'),
    # TOMORROW
    ('kal Patna mein', 'Patna', 'weather'),
    ('kal Patna mein barish hogi', 'Patna', 'weather'),
    ('tomorrow Mumbai weather', 'Mumbai', 'weather'),
    # ACTIVITY
    ('is it good to go for bike ride in Mumbai tomorrow', 'Mumbai', 'weather'),
    ('Can I go cycling in Delhi tomorrow?', 'Delhi', 'weather'),
    ('Is tomorrow good for outdoor events in Patna?', 'Patna', 'weather'),
    ('Is farming spraying suitable tomorrow in Patna?', 'Patna', 'weather'),
    # LANGUAGE
    ('कल पटना में बारिश होगी?', 'Patna', 'weather'),
    ('Patna ka mausam kaisa hai?', 'Patna', 'weather'),
    ('Patna mein aaj temperature kitna hai?', 'Patna', 'weather'),
    # CONVERSATION
    ('kya hal hai', '', 'conversation'),
    ('kya haal hai bhai', '', 'conversation'),
    ('how are you', '', 'conversation'),
    ('tum kaise ho', '', 'conversation'),
    # LOCATION
    ('Punjab ka weather', 'Punjab', 'weather'),
    ('Haryana ka weather', 'Haryana', 'weather'),
    ('Assam ka weather', 'Assam', 'weather'),
    ('Guwahati Assam ka weather', 'Guwahati', 'weather'),
    ('Kapurthala Punjab ka weather', 'Kapurthala', 'weather'),
    # COMPARISON
    ('Delhi aur Mumbai ka weather compare karo', 'vs', 'comparison'),
    # TIME
    ('Tomorrow morning in Mumbai', 'Mumbai', 'weather'),
    ('Sunday evening Delhi weather', 'Delhi', 'weather'),
    # AMBIGUITY
    ('Springfield weather', 'Springfield', 'clarification'),
    # HISTORICAL
    ('kal Patna mein temperature kya tha?', 'Patna', 'weather'),
    ('yesterday Mumbai mein rain hui?', 'Mumbai', 'weather')
]

passed = 0
failed = 0
for q, exp_loc, exp_type in test_cases:
    try:
        r = httpx.post(base_url, json={'query': q, 'location': 'Amritsar'}, timeout=15.0)
        d = r.json()
        resp_type = d.get('response_type')
        loc = d.get('resolved_location', '')
        ans = d.get('grounded_answer', '')
        ok = (resp_type == exp_type) and (exp_loc.lower() in loc.lower() if exp_loc else True)
        status = 'PASS' if ok else 'FAIL'
        if ok:
            passed += 1
        else:
            failed += 1
        print(f'[{status}] Query: "{q}" -> Type: {resp_type} | Loc: {loc}')
        if not ok:
            print(f'   Expected: Type={exp_type}, Loc={exp_loc}')
            print(f'   Answer: {ans[:80]}...')
    except Exception as e:
        failed += 1
        print(f'[FAIL] Query: "{q}" -> Exception: {e}')

print(f'\nTOTAL: {len(test_cases)} | PASSED: {passed} | FAILED: {failed}')
