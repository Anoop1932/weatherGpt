import sys
import httpx

sys.stdout.reconfigure(encoding='utf-8')

base = 'http://127.0.0.1:8000/api/weather/query'
ctx = []

def chat(q):
    global ctx
    r = httpx.post(base, json={'query': q, 'location': 'Amritsar', 'conversation_context': ctx}, timeout=10.0)
    d = r.json()
    ctx.append({'role': 'user', 'content': q})
    ctx.append({'role': 'assistant', 'content': d.get('grounded_answer', '')})
    resp_type = d.get("response_type")
    loc = d.get("resolved_location")
    w = d.get("weather") or {}
    f_date = w.get("forecast_date", "current")
    ans = d.get("grounded_answer", "")
    print(f"Q: {q}")
    print(f"   -> Type: {resp_type} | Loc: {loc} | Date: {f_date}")
    print(f"   -> Ans: {ans[:90]}...\n")

chat("Patna ka weather kaisa hai?")
chat("kal?")
chat("barish?")
chat("bike ride ke liye?")
chat("why?")
chat("Delhi mein kal barish hogi?")
