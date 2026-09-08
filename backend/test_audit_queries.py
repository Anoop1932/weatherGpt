import sys
from app.ai.nlp_parser import nlp_parser

sys.stdout.reconfigure(encoding='utf-8')

queries = [
    'cal Lucknow mein tapman',
    'cal Lucknow ka vedar batao',
    'cal Lucknow ka vedar kaisa rahega',
    'cal Amritsar ka mausam batao',
    'Amritsar Ka vedar Kaisa Rahega cal',
    'Hisar Haryana mein abhi vartman ka tapman kya hai',
    'is it good to go for bike ride in Mumbai tomorrow',
    'kya hal hai',
    'Amritsar Mein Barish kab Hogi',
    'Amritsar aur London Mein tapman Kitna kitna hai compare karo',
    'India mein sabse Jyada Barish kahan hogi',
    'India mein sabse Jyada Barish kaun si jagah per Hogi'
]

for q in queries:
    p = nlp_parser.parse(q)
    cat = p.get('intent_category')
    it = p.get('extracted_intent')
    lang = p.get('detected_language')
    loc = p.get('resolved_location')
    off = p.get('date_offset')
    print(f"Q: {q}")
    print(f"   -> Cat: {cat} | Intent: {it} | Lang: {lang} | Loc: {loc} | Offset: {off}\n")
