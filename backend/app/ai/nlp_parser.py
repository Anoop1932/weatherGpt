import re
import logging
import datetime
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Indian States & Union Territories mapping (Full name, canonical, unambiguous abbreviations)
INDIAN_STATES = {
    "punjab": "Punjab", "pb": "Punjab",
    "bihar": "Bihar", "br": "Bihar",
    "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
    "haryana": "Haryana", "hr": "Haryana",
    "delhi": "Delhi", "dl": "Delhi", "new delhi": "Delhi",
    "rajasthan": "Rajasthan", "rj": "Rajasthan",
    "maharashtra": "Maharashtra", "mh": "Maharashtra",
    "himachal pradesh": "Himachal Pradesh", "hp": "Himachal Pradesh",
    "uttarakhand": "Uttarakhand", "uk": "Uttarakhand", "ua": "Uttarakhand",
    "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh",
    "gujarat": "Gujarat", "gj": "Gujarat",
    "west bengal": "West Bengal", "wb": "West Bengal",
    "tamil nadu": "Tamil Nadu", "tn": "Tamil Nadu",
    "karnataka": "Karnataka",
    "kerala": "Kerala", "kl": "Kerala",
    "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
    "telangana": "Telangana", "ts": "Telangana", "tg": "Telangana",
    "odisha": "Odisha", "orissa": "Odisha", "or": "Odisha",
    "assam": "Assam", "as": "Assam", "asam": "Assam", "असम": "Assam", "অসম": "Assam",
    "arunachal pradesh": "Arunachal Pradesh", "arunachal": "Arunachal Pradesh",
    "jharkhand": "Jharkhand", "jh": "Jharkhand",
    "chhattisgarh": "Chhattisgarh", "cg": "Chhattisgarh", "ch": "Chhattisgarh",
    "goa": "Goa", "ga": "Goa",
    "jammu and kashmir": "Jammu & Kashmir", "jk": "Jammu & Kashmir", "j&k": "Jammu & Kashmir",
    "ladakh": "Ladakh",
    "chandigarh": "Chandigarh", "chd": "Chandigarh"
}

KNOWN_COUNTRIES = {
    "nepal", "bhutan", "bangladesh", "sri lanka", "pakistan", "india", "bharat",
    "uae", "united arab emirates", "spain", "uk", "usa", "united states", "canada", "australia"
}

CITY_SYNONYMS = {
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "bangalore": "Bengaluru",
    "benares": "Varanasi",
    "banaras": "Varanasi",
    "gurgaon": "Gurugram",
    "noida": "Noida",
    "vizag": "Visakhapatnam",
    "gauhati": "Guwahati"
}

# Devanagari city name -> Romanized canonical name mapping
DEVANAGARI_CITY_MAP = {
    "पटना": "Patna",
    "दिल्ली": "Delhi",
    "नई दिल्ली": "New Delhi",
    "मुंबई": "Mumbai",
    "कोलकाता": "Kolkata",
    "चेन्नई": "Chennai",
    "जयपुर": "Jaipur",
    "लखनऊ": "Lucknow",
    "लखनउ": "Lucknow",
    "हैदराबाद": "Hyderabad",
    "बेंगलुरु": "Bengaluru",
    "अमृतसर": "Amritsar",
    "अम्रितसर": "Amritsar",
    "जलंधर": "Jalandhar",
    "लुधियाना": "Ludhiana",
    "चंडीगढ़": "Chandigarh",
    "हिसार": "Hisar",
    "गुवाहाटी": "Guwahati",
    "वाराणसी": "Varanasi",
    "आगरा": "Agra",
    "कानपुर": "Kanpur",
    "पुणे": "Pune",
    "सूरत": "Surat",
    "अहमदाबाद": "Ahmedabad",
    "नागपुर": "Nagpur",
    "शिमला": "Shimla",
    "कपूरथला": "Kapurthala",
    "गया": "Gaya",
    "मुजफ्फरपुर": "Muzaffarpur",
    "भागलपुर": "Bhagalpur",
}

# Devanagari state name -> Canonical state name mapping
DEVANAGARI_STATE_MAP = {
    "बिहार": "Bihar",
    "पंजाब": "Punjab",
    "हरियाणा": "Haryana",
    "दिल्ली": "Delhi",
    "राजस्थान": "Rajasthan",
    "उत्तर प्रदेश": "Uttar Pradesh",
    "महाराष्ट्र": "Maharashtra",
    "असम": "Assam",
    "असाम": "Assam",
}

KNOWN_CITIES = {
    "amritsar", "ludhiana", "patna", "jalandhar", "kapurthala", "delhi", "new delhi",
    "mumbai", "bengaluru", "kolkata", "chennai", "hyderabad", "jaipur", "chandigarh",
    "patiala", "bathinda", "shimla", "srinagar", "lucknow", "varanasi", "agra",
    "gaya", "muzaffarpur", "bhagalpur", "pune", "ahmedabad", "surat", "kanpur", "nagpur",
    "guwahati", "gauhati", "hisar", "nangli", "nangali", "barcelona", "new york", "london", "paris", "tokyo", "dubai", "singapore", "sydney", "toronto"
}

DISTINCTIVE_PUNJABI_WORDS = {
    "meeh", "pavega", "kida", "kina", "hou", "tuhanu", "saade", "pind",
    "dasso", "hovega", "pao", "vekh", "kallh", "kivein", "changa", "satsriakal", "hanji"
}

ROMAN_HINDI_WORDS = {
    "kal", "aaj", "baarish", "barish", "hogi", "hoga", "mausam", "karna", "jaana",
    "chahiye", "hai", "mein", "par", "subah", "shaam", "parso", "parson", "kab", "kya", "ko",
    "kitni", "kitna", "kaisa", "batao", "bata", "rahega", "rahegi", "rahenge",
    "kahan", "kaun", "kaunsi", "jagah", "sabse", "zyada", "jyada", "adhik", "kam"
}

MONTHS_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9, "october": 10, "oct": 10,
    "november": 11, "nov": 11, "december": 12, "dec": 12,
    "सितंबर": 9, "सितम्बर": 9, "अगस्त": 8, "ਅਗਸਤ": 8, "ਸਤੰਬਰ": 9
}

WEEKDAYS_MAP = {
    "monday": 0, "mon": 0, "tuesday": 1, "tue": 1, "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "friday": 4, "fri": 4, "saturday": 5, "sat": 5, "sunday": 6, "sun": 6,
    "सोमवार": 0, "मंगलवार": 1, "बुधवार": 2, "गुरुवार": 3, "शुक्रवार": 4, "शनिवार": 5, "रविवार": 6,
    "ਸੋਮਵਾਰ": 0, "ਮੰਗਲਵਾਰ": 1, "ਬੁੱਧਵਾਰ": 2, "ਵੀਰਵਾਰ": 3, "ਸ਼ੁੱਕਰਵਾਰ": 4, "ਸ਼ਨਿੱਚਰਵਾਰ": 5, "ਐਤਵਾਰ": 6
}

NON_LOCATION_STOPWORDS = {
    # English Adjectives & Quality Words
    "good", "bad", "best", "better", "suitable", "suitability", "likely", "possible", "safe", "unsafe",
    "great", "fine", "nice", "pleasant", "harsh", "extreme", "severe", "perfect",
    # Activity & Event Words
    "outdoor", "indoors", "indoor", "events", "event", "activity", "activities", "picnic",
    "travel", "trip", "journey", "tour", "drive", "farming", "farm", "crops", "crop", "spraying", "spray",
    "khet", "kheton", "khad", "apne", "apna", "apni", "daal", "dal", "kaam", "allowed", "allow", "badhiya",
    "match", "party", "wedding", "shaadi", "function", "outing", "walk", "jog", "outside", "bahar",
    "bike", "ride", "cycling", "cycle", "bicycle", "biking", "riding",
    # Umbrella & Protection
    "umbrella", "ambrella", "amrela", "umbrela", "chhata", "chaata", "raincoat", "carry", "taking", "take",
    # Weather Vocabulary
    "weather", "forecast", "mausam", "mosam", "taapman", "tapman", "vartman", "temperature", "rain", "barish", "baarish",
    "meeh", "shower", "drizzle", "sun", "sunny", "cloud", "cloudy", "wind", "windy", "hawa",
    "storm", "stormy", "fog", "foggy", "dhund", "humidity", "nami", "uv", "visibility", "pressure",
    # Spatial / Geographic non-location nouns (cities, places, areas, shahron)
    "cities", "city", "place", "places", "area", "areas", "shahar", "shahron", "desh", "state", "states",
    # Timing & Onset
    "start", "starting", "timing", "bachna", "shuru", "onset",
    # Time Vocabulary & Transliterations
    "today", "tomorrow", "yesterday", "day", "after", "morning", "evening", "afternoon", "night",
    "tonight", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august", "september",
    "october", "november", "december", "subah", "shaam", "dopahar", "raat", "kal", "aaj", "parso", "parson",
    "cal", "call", "kl", "kallh", "ajj", "is time", "time", "current", "right now", "now", "abhi", "waqt", "din",
    # Auxiliary, Prepositions & Question Connectors
    "is", "are", "am", "was", "were", "be", "been", "being", "will", "would", "could", "should",
    "can", "may", "might", "must", "do", "does", "did", "have", "has", "had",
    "in", "at", "near", "around", "from", "for", "to", "by", "with", "on", "of", "the", "a", "an", "s", "about",
    # Questions, Pronouns, Ranking & Comparison Connectors
    "what", "when", "where", "how", "why", "who", "which", "form", "it", "you", "me", "i",
    "we", "us", "they", "them", "my", "your", "our", "their", "this", "that", "there", "here",
    "ham", "hum", "humne", "humein", "mujhe", "main", "mera", "meri", "mere",
    "aap", "apka", "apki", "apke", "tum", "tumhara", "tumhari", "tumhare", "tumhe", "tumhen", "tuhada", "tera", "teri", "tere",
    "compare", "comparison", "vs", "versus", "aur", "and", "or", "kaunsa", "kaun", "kaunsi", "difference",
    "kahan", "jagah", "sabse", "zyada", "jyada", "adhik", "kam", "highest", "lowest", "most",
    # Additional Noise & Request Words
    "probability", "chance", "chances", "possibility", "sambhavna", "sambhavit", "level", "status", "condition", "conditions",
    "tell", "show", "give", "check", "info", "information", "details", "report", "update", "updates", "stats",
    "naam", "name", "milta", "aata", "chhajje",
    # Conversational Social / Noise Words
    "hal", "haal", "theek", "bhai", "bhaiya", "scene", "mood", "okay", "ok", "doing", "going", "up",
    "something", "anything", "yourself", "myself", "help", "know", "think", "thought", "believe",
    "feel", "guess", "bro", "dude", "friend", "buddy", "kaise", "kaisa", "ho", "na", "sir", "ji",
    "batao", "btao", "pooch", "poochhna", "dasso", "karo", "kya", "r", "u", "are", "there", "chal", "raha", "sab",
    # Motion & Action Verbs
    "lekar", "nikal", "niklu", "nikle", "nikalna", "ja", "jana", "jaana", "chale", "chalna", "sakte", "sakta", "sakti", "chahiye",
    # Tech & Devotional Noise
    "visual", "studio", "code", "mata", "di", "jai", "shree", "ram", "radhe",
    # Hindi/Punjabi postpositions, grammar particles & auxiliary
    "ka", "ki", "ke", "mein", "me", "se", "ko", "par", "vich", "da", "de", "di", "nu", "liye", "khatir",
    "hogi", "hoga", "hovega", "kitna", "kitni", "hai", "hain", "si", "tha", "thi", "the", "hui",
    "rahega", "rahegi", "rahenge", "kab",
    # Hinglish Weather Word Variations
    "vedar", "wether", "weathr", "wheather", "weathar",
    # Devanagari stopwords (time, weather, question, auxiliary)
    "कल", "आज", "परसों", "बारिश", "मौसम", "तापमान", "में", "का", "की", "के", "क्या",
    "होगी", "होगा", "है", "हैं", "कैसा", "कितना", "कितनी",
    "था", "थी", "थे", "हुई", "पर", "से", "को", "बाहर", "छाता",
    "वर्तमान", "अभी", "सुबह", "शाम", "दोपहर", "रात",
    "मौसम", "हवा", "धूप", "बादल", "गर्मी", "ठंड", "सबसे", "ज्यादा", "ज़्यादा", "कहाँ", "कौन",
    "शहरों", "शहर", "खेत", "खाद", "स्प्रे", "बढ़िया", "बचना"
}


def normalize_query_text(query: str) -> str:
    """
    Normalizes speech-to-text variations and common transliteration typos before NLP classification.
    """
    q = query.strip()
    # Normalize common transliterations of weather words
    q = re.sub(r'\b(vedar|wheather|weathar|wether|weathr)\b', 'weather', q, flags=re.IGNORECASE)
    q = re.sub(r'\bbaarish\b', 'barish', q, flags=re.IGNORECASE)
    q = re.sub(r'\btaapman\b', 'tapman', q, flags=re.IGNORECASE)
    q = re.sub(r'\bmosam\b', 'mausam', q, flags=re.IGNORECASE)
    q = re.sub(r'\bpanjab\b', 'punjab', q, flags=re.IGNORECASE)
    q = re.sub(r'\basam\b', 'assam', q, flags=re.IGNORECASE)
    q = re.sub(r'\bkallh\b', 'kal', q, flags=re.IGNORECASE)
    q = re.sub(r'\bparson\b', 'parso', q, flags=re.IGNORECASE)
    # Speech-recognition and Hinglish transliterations of tomorrow: "cal", "call", "kl" -> "kal"
    q = re.sub(r'\b(cal|call|kl)\b', 'kal', q, flags=re.IGNORECASE)
    # Normalize umbrella variants
    q = re.sub(r'\b(ambrella|amrela|umbrela|chhata|chata|chatta)\b', 'umbrella', q, flags=re.IGNORECASE)
    # Strip conversational chhajje
    q = re.sub(r'\bchhajje\b', '', q, flags=re.IGNORECASE)
    return q


def is_gibberish(query: str) -> bool:
    """
    Detects random, unparseable, keyboard-mashed or gibberish queries.
    """
    q_clean = query.strip()
    if not q_clean:
        return True

    q_low = q_clean.lower()

    # 1. 5+ consecutive consonants without vowels in Latin characters
    if re.search(r'[bcdfghjklmnpqrstvwxyz]{5,}', q_low):
        return True

    # 2. Keyboard pattern mashing
    keyboard_patterns = ["asdf", "dfgh", "fghj", "ghjk", "hjkl", "qwert", "werty", "ertyu", "rtyui", "tyuio", "yuiop", "zxcv", "xcvb", "cvbn", "vbnm"]
    if any(pat in q_low for pat in keyboard_patterns) and not any(w in q_low for w in ["weather", "vedar", "wether", "rain", "barish", "mausam"]):
        return True

    # 3. High length word with no vowels (length >= 7 and no vowels)
    words = re.findall(r'\b[A-Za-z\u0900-\u097f\u0a00-\u0a7f]+\b', q_clean)
    for word in words:
        if len(word) >= 7 and not re.search(r'[aeiouy\u0900-\u097f\u0a00-\u0a7f]', word.lower()):
            return True

    return False


class NLPQueryParser:

    def detect_language(self, query: str) -> str:
        """
        Detects message language:
        - Gurmukhi script or distinctive Roman Punjabi -> 'pa'
        - Devanagari script or Roman Hindi / Hinglish -> 'hi'
        - English -> 'en'
        """
        if re.search(r'[\u0A00-\u0A7F]', query):
            return "pa"

        if re.search(r'[\u0900-\u097F]', query):
            return "hi"

        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        distinctive_pa = query_words.intersection(DISTINCTIVE_PUNJABI_WORDS)
        hindi_matches = query_words.intersection(ROMAN_HINDI_WORDS)

        if len(distinctive_pa) > 0 and len(distinctive_pa) >= len(hindi_matches):
            return "pa"

        if len(hindi_matches) >= 1:
            return "hi"

        return "en"

    def classify_intent_category(self, query: str) -> str:
        """
        Classifies user message into standard intent categories:
        - GREETING
        - CONVERSATION
        - HELP/CAPABILITY
        - WEATHER_CURRENT
        - WEATHER_FORECAST
        - WEATHER_RAIN
        - WEATHER_TEMPERATURE
        - WEATHER_HUMIDITY
        - WEATHER_WIND
        - WEATHER_CONDITION
        - WEATHER_WARNING
        - ACTIVITY_SUITABILITY
        - AGRICULTURE
        - OUTDOOR_EVENT
        - CYCLING/BIKE_RIDE
        - COMPARISON
        - RANKING
        - HISTORICAL_WEATHER
        - LOCATION_ONLY
        - FOLLOW_UP
        - UNCLEAR
        """
        normalized_q = normalize_query_text(query)
        q_lower = normalized_q.lower().strip()

        # 1. Gibberish / Unclear Check
        if is_gibberish(normalized_q):
            return "UNCLEAR"

        # Explicit Unclear Query Fragments (e.g. "umbrella is", "is which form in Amritsar", or incomplete phrases)
        if re.search(r'\bumbrella\s+is\b', q_lower) or re.search(r'\bis\s+which\s+form\b', q_lower) or re.search(r'\bwhich\s+form\b', q_lower):
            return "UNCLEAR"

        # 2. Non-weather software / coding / tech questions (e.g. "Visual Studio code kahan per Milta Hai")
        if any(ph in q_lower for ph in ["visual studio", "vs code", "vscode", "kahan per milta hai", "kahan milta hai", "download visual", "download code"]):
            return "NON_WEATHER"

        # 3. Identity Queries (e.g. "tumhara naam kya hai", "what is your name", "who are you")
        if any(ph in q_lower for ph in [
            "tumhara naam", "naam kya hai", "apka naam", "what is your name", "who are you",
            "who r u", "tum kaun ho", "aap kaun ho", "tusi kaun ho", "what are you called"
        ]):
            return "IDENTITY"

        # 4. Capabilities Queries (e.g. "Tumhen Kya Aata Hai", "what can you do")
        if any(ph in q_lower for ph in [
            "tumhen kya aata hai", "tumhe kya aata hai", "kya aata hai", "what can you do",
            "kya kar sakte ho", "tum kya kar sakte ho", "aap kya kar sakte ho", "what are your capabilities",
            "what features do you have"
        ]):
            return "CAPABILITIES"

        # 5. Devotional and Traditional Greetings (e.g. "jai mata di", "ram ram")
        if re.search(r'\b(jai\s+mata\s+di|jai\s+shree\s+ram|radhe\s+radhe|har\s+har\s+mahadev|om\s+namah\s+shivay)\b', q_lower):
            return "GREETING"

        # 6. Standard Greetings
        if re.search(r'\b(hello|hi|hey|good morning|good evening|good night|namaste|namaskar|sat sri akal|pranam|what\'s up|sup)\b', q_lower) and not any(w in q_lower for w in ["weather", "barish", "rain", "mausam", "temp", "tapman"]):
            return "GREETING"

        # 7. Non-weather Conversational / Social
        conversational_patterns = [
            r"\bkya\s+h[a|aa]*l\b",
            r"\bh[a|aa]+l\s+hai\b",
            r"\bhow\s+are\s+you\b",
            r"\bhow\s+are\s+you\s+doing\b",
            r"\bhow\s+is\s+it\s+going\b",
            r"\bhow\'?s\s+it\s+going\b",
            r"\bhow\s+are\s+things\b",
            r"\bare\s+you\s+okay\b",
            r"\bare\s+you\s+doing\s+okay\b",
            r"\btum\s+theek\s+ho\b",
            r"\btheek\s+ho\s+na\b",
            r"\btheek\s+ho\b",
            r"\bsab\s+theek\b",
            r"\bkaise\s+ho\b",
            r"\bkaisa\s+hai\b",
            r"\btum\s+kaise\s+ho\b",
            r"\bbhai\s+kya\s+scene\b",
            r"\bkya\s+scene\s+hai\b",
            r"\bkya\s+chal\s+raha\b",
            r"\baaj\s+mood\s+kaisa\b",
            r"\bwhat\'?s\s+up\b",
            r"\bwassup\b",
            r"\bdoing\s+great\b",
            r"\bdoing\s+well\b"
        ]
        if any(re.search(pat, q_lower) for pat in conversational_patterns) and not any(w in q_lower for w in ["weather", "barish", "rain", "mausam", "temp", "tapman"]):
            return "CONVERSATION"

        # 8. Help Queries
        if any(ph in q_lower for ph in ["help me", "can you help me", "need help", "madad"]):
            return "HELP"

        # 9. Thanks / Acknowledgement
        if re.search(r'\b(thank you|thanks|shukriya|dhanyawad|dhanwad|thanku|bye|goodbye)\b', q_lower):
            return "CONVERSATION"

        # 9b. User Contradiction / Discrepancy Challenge (e.g. "tumne pahle 10% kaha tha ab 100% bol rahe ho")
        contradiction_patterns = [
            r'\b(?:tumne|pehle|pahle|aapne|you\s+said|you\s+told)\b.*\b(?:kaha|bola|bataya|said|bol\s+rahe|keh\s+rahe)\b',
            r'\b(?:pehle|pahle)\s+to\s+tumne\b',
            r'\b(?:pehle|pahle)\s+kuch\s+aur\b',
            r'\bwhy\s+did\s+you\s+change\b',
            r'\bwhy\s+are\s+you\s+saying\s+different\b',
            r'\b(?:earlier|previously)\s+you\s+said\b',
            r'\bcontradict\b'
        ]
        if any(re.search(pat, q_lower) for pat in contradiction_patterns):
            return "CONTRADICTION_CHALLENGE"

        # 10. Travel Route Check (e.g. "Delhi se Mumbai bike par travel kar sakta hun aaj?", "Kal Amritsar se Jalandhar bike se jaana safe rahega?")
        travel_route_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+se\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if not travel_route_match:
            travel_route_match = re.search(r'\bfrom\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+to\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if travel_route_match:
            o_cand, d_cand = travel_route_match.group(1).lower(), travel_route_match.group(2).lower()
            if o_cand not in NON_LOCATION_STOPWORDS and d_cand not in NON_LOCATION_STOPWORDS:
                if any(w in q_lower for w in ["travel", "bike", "ride", "jaana", "jana", "cycling", "cycle", "drive", "safe", "trip"]):
                    return "TRAVEL"

        # 11. Regional Comparison Clarification (e.g. "India ke shahron ko compare karo", "India ke sabhi shahron ka comparison karo weather ke hisab se")
        if any(w in q_lower for w in ["compare", "comparison"]) and any(w in q_lower for w in ["shahron", "cities", "places", "areas"]) and not re.search(r'\b(?:aur|and|vs|versus)\b', q_lower):
            return "REGIONAL_COMPARISON_CLARIFICATION"

        # 12. Multi-Location Comparison Check (Must NOT be routed to regional ranking)
        # e.g. "Mumbai aur Delhi mein kis jagah barish ki sambhavna jyada hai", "Amritsar aur Delhi compare karo", "India aur Dubai ka temperature compare karo"
        multi_loc_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+(?:aur|and|vs|versus)\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if multi_loc_match:
            c1_cand, c2_cand = multi_loc_match.group(1).lower(), multi_loc_match.group(2).lower()
            if c1_cand not in NON_LOCATION_STOPWORDS and c2_cand not in NON_LOCATION_STOPWORDS:
                return "COMPARISON"
        if any(w in q_lower for w in ["compare", "comparison", "difference", "kaunsa din", "better hai", "kaun sa din", "vs", "versus"]):
            return "COMPARISON"

        # 13. Rain timing onset & Outdoor timing check
        if re.search(r'\b(rain\s+kab\s+start|barish\s+kab\s+start|barish\s+kab\s+hogi|when\s+will\s+it\s+rain|kab\s+start\s+hone|start\s+hone\s+ki\s+possibility|when\s+can\s+i\s+expect\s+rain)\b', q_lower):
            return "RAIN_TIMING"
        if any(ph in q_lower for ph in ["barish se bachna", "badhiya time", "best time to go out", "dry window"]):
            return "OUTDOOR_TIMING"

        # 13b. Peak Rain / Temperature Forecast Day for a single place across upcoming days
        # e.g. "Amritsar mein kaun se din sabse zyada baarish hogi", "which day will have the most rain in Amritsar"
        peak_day_patterns = [
            r'\b(?:kaun\s+se\s+din|kaun\s+sa\s+din|kis\s+din|which\s+day|what\s+day)\b.*\b(?:sabse\s+zyada|sabse\s+jyada|most|highest|peak|maximum)\b',
            r'\b(?:sabse\s+zyada|sabse\s+jyada|most|highest|peak|maximum)\b.*\b(?:kaun\s+se\s+din|kaun\s+sa\s+din|kis\s+din|which\s+day|what\s+day)\b',
            r'\b(?:highest|peak|maximum)\s+rain(?:fall)?\s+day\b',
            r'\bwhich\s+day\b.*\bmost\s+rain\b'
        ]
        if any(re.search(pat, q_lower) for pat in peak_day_patterns):
            return "FORECAST_PEAK_DAY"

        # 14. Regional Ranking / Extremes / Spatial Analysis
        ranking_patterns = [
            r'\bsabse\s+(?:zyada|jyada|adhik|kam)\b',
            r'\b(kahan|kahan\s+per|kahan\s+par|kis\s+jagah|kis\s+shahar|kis\s+city|kis\s+state)\b.*\b(?:hogi|hoga|ho\s+rahi|barish|rain)\b',
            r'\bke\s+kaun\s+se\s+cities\b',
            r'\bmost\s+(?:rain|rainfall|rainy|hot|cold)\b',
            r'\bhighest\s+(?:rain|rainfall|precipitation|temperature|temp)\b',
            r'\blowest\s+(?:temperature|temp|rain)\b',
            r'\bhottest\b',
            r'\bcoldest\b',
            r'\bwettest\b',
            r'\bmaximum\s+barish\b'
        ]
        if any(re.search(pat, q_lower) for pat in ranking_patterns):
            return "RANKING"

        # 15. Historical Weather (Past Tense Check)
        past_markers = [r'\byesterday\b', r'\bkal\b.*\b(tha|thi|the|si|kya\s+tha|hui\s+thi)\b', r'\bpichle\b', r'\bpast\b']
        if any(re.search(pat, q_lower) for pat in past_markers):
            return "HISTORICAL_WEATHER"

        # 16. Cycling / Bike Ride Activity
        if any(w in q_lower for w in ["bike ride", "cycling", "bike", "bicycle", "cycle", "riding", "biking"]):
            return "BIKE_RIDE" if "bike" in q_lower else "CYCLING"

        # 17. Agriculture / Farming / Spraying / Fertilizer (khad)
        if any(w in q_lower for w in ["spraying", "spray", "crop", "crops", "kheti", "farmer", "farming", "pesticide", "fertilizer", "kisaan", "chhidkaw", "khad", "khet", "kheton"]):
            return "AGRICULTURE"

        # 18. Outdoor Event
        if any(w in q_lower for w in ["outdoor event", "outdoor events", "wedding", "match", "party", "function", "shaadi"]):
            return "OUTDOOR_EVENT"

        # 19. Activity Suitability (Umbrella Carrying & Going Outside)
        umbrella_activity_patterns = [
            r'\bumbrella\b.*\b(?:lekar|nikal|niklu|ja\s+sakte|carry|take|bahar|outside)\b',
            r'\b(?:lekar|carry|take)\b.*\bumbrella\b',
            r'\b(?:bahar|outside)\b.*\b(?:jana|ja\s+sakte|nikal|niklu)\b',
            r'\bshould\s+i\s+carry\s+an\s+umbrella\b',
            r'\bcan\s+i\s+go\s+outside\b',
            r'\bkal\s+bahar\s+jana\s+theek\s+rahega\b',
            r'\bumbrella\s+lekar\s+niklu\b',
            r'\bbaarish\s+mein\s+bahar\s+ja\s+sakte\b',
            r'\bbahar\s+jana\s+safe\s+hai\b',
            r'\bbahar\s+jana\s+(?:theek|sahi|safe)\b',
            r'\b(?:safe|theek|sahi)\s+hai\s+bahar\s+jana\b'
        ]
        if any(re.search(pat, q_lower) for pat in umbrella_activity_patterns):
            return "ACTIVITY_SUITABILITY"

        # 20. General Activity / Travel Suitability
        if any(w in q_lower for w in ["picnic", "travel", "jaana", "trip", "drive", "safari", "outing", "running", "jog", "walk", "outdoor", "outdoors"]):
            return "ACTIVITY_SUITABILITY"

        # 21. Current Weather (Real-time continuous rain, abhi/vartman)
        continuous_current_patterns = [
            r'\bis\s+rain\s+is\s+happening\b',
            r'\bis\s+rain\s+happening\b',
            r'\bis\s+it\s+raining\b',
            r'\bbarish\s+ho\s+rahi\s+hai\b',
            r'\bho\s+rahi\s+hai\b',
            r'\babhi\b',
            r'\bvartman\b',
            r'\bright\s+now\b',
            r'\bcurrent\b',
            r'\bis\s+time\b',
            r'\bis\s+waqt\b'
        ]
        if any(re.search(pat, q_lower) for pat in continuous_current_patterns):
            return "WEATHER_CURRENT"

        # 22. Specific Weather Parameters
        if any(w in q_lower for w in ["rain", "barish", "meeh", "shower", "drizzle", "umbrella", "precipitation"]):
            return "WEATHER_RAIN"
        if any(w in q_lower for w in ["temperature", "tapman", "garmi", "thand", "temp", "hot", "cold", "maximum", "minimum"]):
            return "WEATHER_TEMPERATURE"
        if any(w in q_lower for w in ["humidity", "nami"]):
            return "WEATHER_HUMIDITY"
        if any(w in q_lower for w in ["wind", "hawa", "tez hawa", "breeze"]):
            return "WEATHER_WIND"
        if any(w in q_lower for w in ["warning", "alert", "danger", "storm", "cyclone", "toofan"]):
            return "WEATHER_WARNING"
        if any(w in q_lower for w in ["cloud", "cloudy", "fog", "foggy", "dhund", "clear sky", "condition"]):
            return "WEATHER_CONDITION"

        # 23. Location-only query (e.g. "Amritsar", "Delhi", "Patna, Bihar")
        raw_words = re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', q_lower)
        clean_words = [w for w in raw_words if w not in NON_LOCATION_STOPWORDS]
        if len(raw_words) <= 3 and len(clean_words) >= 1 and all(w.lower() in KNOWN_CITIES or w.lower() in INDIAN_STATES or w.lower() in CITY_SYNONYMS or w.lower() in KNOWN_COUNTRIES for w in clean_words):
            return "LOCATION_ONLY"

        # 24. Short follow-up query (e.g. "kal?", "barish?", "bike ride ke liye?", "why?", "What about Sunday?", "Compare it with Delhi.")
        has_known_place = any(w.lower() in KNOWN_CITIES or w.lower() in INDIAN_STATES or w.lower() in CITY_SYNONYMS or w.lower() in KNOWN_COUNTRIES for w in clean_words)
        if not has_known_place and len(raw_words) <= 6 and any(w in q_lower for w in [
            "kal", "tomorrow", "today", "aaj", "parso", "why", "kyun", "barish", "rain", "bike", "ride",
            "what about", "and rain", "how much", "kitna", "kitni", "wahan", "yahan", "iske kal", "what if", "sunday", "farming", "temperature"
        ]):
            return "FOLLOW_UP"

        return "WEATHER_FORECAST"

    def classify_intent(self, query: str) -> str:
        """
        Classifies intent into granular programmatic keys compatible with grounded engine.
        """
        cat = self.classify_intent_category(query)
        q_lower = normalize_query_text(query).lower()

        if cat == "GREETING":
            return "non_weather_greeting"
        elif cat == "IDENTITY":
            return "identity"
        elif cat == "CAPABILITIES":
            return "capability"
        elif cat == "HELP":
            return "help"
        elif cat == "NON_WEATHER":
            return "non_weather"
        elif cat == "CONVERSATION":
            if re.search(r'\b(thank you|thanks|shukriya|dhanyawad)\b', q_lower):
                return "non_weather_thanks"
            return "non_weather_conversation"
        elif cat == "UNCLEAR":
            return "unclear_gibberish"
        elif cat == "TRAVEL":
            if any(w in q_lower for w in ["bike", "cycling", "cycle"]):
                return "bike_ride"
            return "travel"
        elif cat == "REGIONAL_COMPARISON_CLARIFICATION":
            return "regional_comparison_clarification"
        elif cat == "RAIN_TIMING":
            return "rain_timing"
        elif cat == "OUTDOOR_TIMING":
            return "outdoor_timing"
        elif cat in ["CYCLING", "BIKE_RIDE", "CYCLING/BIKE_RIDE"]:
            return "cycling" if cat == "CYCLING" else "bike_ride"
        elif cat == "CONTRADICTION_CHALLENGE":
            return "contradiction_challenge"
        elif cat == "FORECAST_PEAK_DAY":
            return "forecast_peak_day"
        elif cat == "AGRICULTURE":
            if "khad" in q_lower or "fertilizer" in q_lower or "urea" in q_lower:
                return "agriculture_fertilizer"
            if "spraying" in q_lower or "spray" in q_lower or "chhidkaw" in q_lower or "pesticide" in q_lower:
                return "agriculture_spraying"
            if "sinchai" in q_lower or "irrigation" in q_lower or "paani" in q_lower:
                return "agriculture_irrigation"
            return "agriculture"
        elif cat == "OUTDOOR_EVENT":
            return "event"
        elif cat == "ACTIVITY_SUITABILITY":
            if "umbrella" in q_lower or "chhata" in q_lower or "raincoat" in q_lower:
                return "umbrella"
            if any(w in q_lower for w in ["travel", "trip", "journey", "drive", "jaana"]):
                return "travel"
            return "outdoor_activity"
        elif cat == "COMPARISON":
            return "comparison"
        elif cat == "RANKING":
            return "ranking"
        elif cat == "HISTORICAL_WEATHER":
            return "historical_weather"
        elif cat == "WEATHER_CURRENT":
            if any(w in q_lower for w in ["rain", "barish", "meeh", "shower", "raining"]):
                return "rain"
            if any(w in q_lower for w in ["temperature", "tapman", "temp"]):
                return "temperature"
            return "current_weather"
        elif cat == "WEATHER_RAIN":
            if re.search(r'\b(kab\s+hogi|kab\s+hoga|kab\s+aayegi|kab\s+tak|when\s+will|what\s+time|kis\s+samay|kis\s+time)\b', q_lower):
                return "rain_timing"
            return "rain"
        elif cat == "WEATHER_TEMPERATURE":
            return "temperature"
        elif cat == "WEATHER_HUMIDITY":
            return "humidity"
        elif cat == "WEATHER_WIND":
            return "wind"
        elif cat == "WEATHER_WARNING":
            return "warning"
        return "forecast"

    def extract_location_and_state(
        self,
        query: str,
        last_location: Optional[str] = None
    ) -> Tuple[str, Optional[str], bool, bool, bool]:
        """
        Extracts location & state dynamically using strong location signals (prepositions, recognized city/state lookup).
        Returns:
        (resolved_location, extracted_state, has_explicit_location, is_state_query, missing_location)
        """
        norm_query = normalize_query_text(query)
        q_lower = re.sub(r"'s\b", "", norm_query.lower().strip())

        # If query is non-weather conversation, greeting, identity, capabilities, help, meta, or gibberish, do NOT extract location
        cat = self.classify_intent_category(norm_query)
        if cat in ["GREETING", "CONVERSATION", "IDENTITY", "CAPABILITIES", "HELP", "NON_WEATHER", "UNCLEAR"]:
            return "", None, False, False, True

        # Special check for regional comparison clarification ("India ke shahron ko compare karo")
        if cat == "REGIONAL_COMPARISON_CLARIFICATION":
            return "India", "India", True, True, False

        # Special check for RANKING queries ("India mein sabse zyada barish kahan hogi", "Punjab ke kaun se cities mein barish hogi")
        if cat == "RANKING":
            scope = "India"
            for state_key, state_canonical in INDIAN_STATES.items():
                if re.search(r'\b' + re.escape(state_key) + r'\b', q_lower):
                    scope = state_canonical
                    break
            return scope, scope, True, True, False

        # Travel Route Extraction ("Delhi se Mumbai bike par travel kar sakta hun aaj?")
        travel_route_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+se\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if not travel_route_match:
            travel_route_match = re.search(r'\bfrom\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+to\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if travel_route_match:
            o_cand, d_cand = travel_route_match.group(1).title(), travel_route_match.group(2).title()
            if o_cand.lower() not in NON_LOCATION_STOPWORDS and d_cand.lower() not in NON_LOCATION_STOPWORDS:
                return f"{o_cand} to {d_cand}", None, True, False, False

        # Early Devanagari city name detection: transliterate known Devanagari city names to romanized form
        for dev_city, roman_city in DEVANAGARI_CITY_MAP.items():
            if dev_city in norm_query:
                # Check for Devanagari state names too
                dev_state = None
                for dev_st, roman_st in DEVANAGARI_STATE_MAP.items():
                    if dev_st in norm_query and dev_st != dev_city:
                        dev_state = roman_st
                        break
                if dev_state:
                    return f"{roman_city}, {dev_state}", dev_state, True, False, False
                return roman_city, None, True, False, False

        # Also check for Devanagari state-only queries (e.g. "बिहार का मौसम")
        for dev_st, roman_st in DEVANAGARI_STATE_MAP.items():
            if dev_st in norm_query:
                if dev_st not in DEVANAGARI_CITY_MAP:
                    return roman_st, roman_st, True, True, False

        extracted_state = None

        # Check for explicit state mention in query (e.g. "Arunachal Pradesh ka weather", "Asam ka weather")
        for state_key, state_canonical in INDIAN_STATES.items():
            if re.search(r'\b' + re.escape(state_key) + r'\b', q_lower):
                extracted_state = state_canonical
                break

        # Check for multi-location comparison, e.g., "Delhi aur Mumbai", "Delhi and Mumbai", "Amritsar aur Delhi"
        multi_loc_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+(?:aur|and|vs|versus)\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
        if multi_loc_match:
            c1, c2 = multi_loc_match.group(1).title(), multi_loc_match.group(2).title()
            if c1.lower() not in NON_LOCATION_STOPWORDS and c2.lower() not in NON_LOCATION_STOPWORDS:
                return c1, extracted_state, True, False, False

        # Follow-up comparison check: "Compare it with Delhi."
        if (cat == "COMPARISON" or "compare" in q_lower) and last_location:
            comp_with_match = re.search(r'\b(?:with|se|aur|and)\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', q_lower)
            if comp_with_match:
                cand_comp = comp_with_match.group(1).title()
                if cand_comp.lower() not in NON_LOCATION_STOPWORDS and (cand_comp.lower() in KNOWN_CITIES or cand_comp.lower() in CITY_SYNONYMS or cand_comp.lower() in INDIAN_STATES or cand_comp.lower() in KNOWN_COUNTRIES):
                    return last_location, extracted_state, True, False, False

        # Check for city synonyms (e.g. Bombay -> Mumbai)
        for syn_key, syn_canonical in CITY_SYNONYMS.items():
            if re.search(r'\b' + re.escape(syn_key) + r'\b', q_lower):
                return syn_canonical, extracted_state, True, False, False

        # Check for Nangli locality in Amritsar (e.g. "Amritsar ki Nangli", "Nangli Amritsar")
        if "nangli" in q_lower or "nangali" in q_lower:
            return "Nangli, Amritsar", "Punjab", True, False, False

        # 1. Preposition Location Signals (English) - e.g. "in Barcelona, Catalonia, Spain", "in Mumbai"
        prep_match = re.search(r'\b(?:in|at|near|around)\s+([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s,]+)', q_lower)
        if prep_match:
            candidate_raw = prep_match.group(1).strip()
            # If comma-separated, preserve comma structure for multi-tier geocoding (e.g. Barcelona, Catalonia, Spain)
            if "," in candidate_raw:
                segments = [s.strip() for s in candidate_raw.split(",") if s.strip()]
                clean_segments = []
                for seg in segments:
                    seg_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', seg) if w.lower() not in NON_LOCATION_STOPWORDS]
                    if seg_words:
                        clean_segments.append(" ".join(seg_words))
                if clean_segments:
                    full_loc = ", ".join(clean_segments)
                    return full_loc, extracted_state, True, False, False
            prep_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', candidate_raw) if w.lower() not in NON_LOCATION_STOPWORDS]
            if prep_words:
                clean_city_words = [w for w in prep_words if (not extracted_state or w.lower() != extracted_state.lower()) and w.lower() not in INDIAN_STATES]
                if clean_city_words:
                    city_name = " ".join(clean_city_words)
                    city_low = city_name.lower()
                    if city_low in KNOWN_CITIES or city_low in CITY_SYNONYMS or city_low in KNOWN_COUNTRIES:
                        if extracted_state:
                            return f"{city_name}, {extracted_state}", extracted_state, True, False, False
                        return city_name, extracted_state, True, False, False
                elif extracted_state:
                    return extracted_state, extracted_state, True, True, False

        # 2. Hindi/Punjabi postpositions e.g. "Amritsar mein", "Patna vich", "Jalandhar da", "Delhi ko", "Guwahati Asam ka"
        post_match = re.search(r'\b([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+?)\s+(?:mein|vich|da|de|di|nu|ka|ki|ke|par|ko)\b', q_lower)
        if post_match:
            candidate_raw = post_match.group(1).strip()
            post_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', candidate_raw) if w.lower() not in NON_LOCATION_STOPWORDS]
            if post_words:
                clean_city_words = [w for w in post_words if (not extracted_state or w.lower() != extracted_state.lower()) and w.lower() not in INDIAN_STATES]
                if clean_city_words:
                    city_name = " ".join(clean_city_words)
                    city_low = city_name.lower()
                    if city_low in KNOWN_CITIES or city_low in CITY_SYNONYMS or city_low in KNOWN_COUNTRIES:
                        if extracted_state:
                            return f"{city_name}, {extracted_state}", extracted_state, True, False, False
                        return city_name, extracted_state, True, False, False
                elif extracted_state:
                    return extracted_state, extracted_state, True, True, False

        # Check for recognized standalone countries (e.g. "Nepal ka weather dikhao")
        for country in KNOWN_COUNTRIES:
            if re.search(r'\b' + re.escape(country) + r'\b', q_lower):
                c_name = "United Arab Emirates" if country in ["uae", "united arab emirates"] else country.title()
                return c_name, None, True, False, False

        # 3. Location preceding weather keyword, e.g. "New York weather", "Delhi weather", "Patna weather"
        weather_match = re.search(r'([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)\s+(?:weather|mausam|forecast)\b', q_lower)
        if weather_match:
            candidate_raw = weather_match.group(1).strip()
            w_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', candidate_raw) if w.lower() not in NON_LOCATION_STOPWORDS]
            if w_words:
                clean_city_words = [w for w in w_words if (not extracted_state or w.lower() != extracted_state.lower()) and w.lower() not in INDIAN_STATES]
                if clean_city_words:
                    city_name = " ".join(clean_city_words)
                    city_low = city_name.lower()
                    if city_low in KNOWN_CITIES or city_low in CITY_SYNONYMS or city_low in KNOWN_COUNTRIES:
                        if extracted_state:
                            return f"{city_name}, {extracted_state}", extracted_state, True, False, False
                        return city_name, extracted_state, True, False, False
                elif extracted_state:
                    return extracted_state, extracted_state, True, True, False

        # 4. Check for known cities/states in token list (Strict Signal Validation)
        # NEVER let arbitrary sentence words (carry, start, cities, umbrella, khad, khet) become locations!
        words = re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', q_lower)
        candidate_words = []
        for word in words:
            w_clean = word.lower()
            if w_clean in NON_LOCATION_STOPWORDS:
                continue
            if extracted_state and (w_clean == extracted_state.lower() or w_clean in INDIAN_STATES):
                continue
            candidate_words.append(word.title())

        # Validate candidate place name against established location entities
        if candidate_words:
            clean_city_words = [w for w in candidate_words if (not extracted_state or w.lower() != extracted_state.lower()) and w.lower() not in INDIAN_STATES]
            if clean_city_words:
                city_name = " ".join(clean_city_words)
                city_low = city_name.lower()
                if city_low in KNOWN_CITIES or city_low in CITY_SYNONYMS or city_low in KNOWN_COUNTRIES:
                    if extracted_state:
                        return f"{city_name}, {extracted_state}", extracted_state, True, False, False
                    return city_name, extracted_state, True, False, False
                elif cat == "LOCATION_ONLY" and len(clean_city_words) == 1:
                    if extracted_state:
                        return f"{city_name}, {extracted_state}", extracted_state, True, False, False
                    return city_name, extracted_state, True, False, False
            elif extracted_state:
                return extracted_state, extracted_state, True, True, False

        # If no city name, but an explicit state was mentioned (e.g., "Punjab ka weather", "Assam ka weather", "Arunachal Pradesh ka weather")
        if extracted_state:
            return extracted_state, extracted_state, True, True, False

        # 5. Conversation Follow-up Context: use last_location ONLY if no explicit location exists in query
        if last_location and last_location.strip() and cat not in ["GREETING", "HELP/CAPABILITY", "HELP", "CONVERSATION", "IDENTITY", "CAPABILITIES", "NON_WEATHER", "UNCLEAR"]:
            return last_location.strip(), None, False, False, False

        # Missing location entirely
        return "", None, False, False, True

    def extract_date_offset(
        self,
        query: str,
        last_date: Optional[str] = None
    ) -> Tuple[int, str, bool]:
        """
        Returns (days_offset, date_label, is_out_of_range)
        """
        norm_query = normalize_query_text(query)
        today = datetime.date.today()
        q_lower = norm_query.lower()

        # 1. Past context check ("kal ... kya tha", "yesterday", "hui thi")
        past_markers = [r'\byesterday\b', r'\bkal\b.*\b(tha|thi|the|si|kya\s+tha|hui\s+thi)\b', r'\bpichle\b', r'\bpast\b']
        if any(re.search(pat, q_lower) for pat in past_markers):
            yesterday = today - datetime.timedelta(days=1)
            return -1, yesterday.strftime("%Y-%m-%d"), False

        # 2. Check for numeric date + month, e.g., "15 September", "september 15"
        date_num_month = re.search(r'(\d{1,2})\s+([a-z\u0900-\u097f\u0a00-\u0a7f]+)', q_lower)
        month_date_num = re.search(r'([a-z\u0900-\u097f\u0a00-\u0a7f]+)\s+(\d{1,2})', q_lower)

        target_date = None

        if date_num_month and date_num_month.group(2) in MONTHS_MAP:
            day_val = int(date_num_month.group(1))
            month_val = MONTHS_MAP[date_num_month.group(2)]
            year_val = today.year
            try:
                target_date = datetime.date(year_val, month_val, day_val)
                if target_date < today - datetime.timedelta(days=1):
                    target_date = datetime.date(year_val + 1, month_val, day_val)
            except ValueError:
                pass
        elif month_date_num and month_date_num.group(1) in MONTHS_MAP:
            day_val = int(month_date_num.group(2))
            month_val = MONTHS_MAP[month_date_num.group(1)]
            year_val = today.year
            try:
                target_date = datetime.date(year_val, month_val, day_val)
                if target_date < today - datetime.timedelta(days=1):
                    target_date = datetime.date(year_val + 1, month_val, day_val)
            except ValueError:
                pass

        if not target_date:
            for day_name, day_idx in WEEKDAYS_MAP.items():
                if day_name in q_lower:
                    days_ahead = (day_idx - today.weekday()) % 7
                    if days_ahead == 0 and ("next" in q_lower or "agle" in q_lower):
                        days_ahead = 7
                    target_date = today + datetime.timedelta(days=days_ahead)
                    break

        if not target_date:
            if "day after tomorrow" in q_lower or "parso" in q_lower:
                target_date = today + datetime.timedelta(days=2)
            elif "tomorrow" in q_lower or "kal" in q_lower:
                target_date = today + datetime.timedelta(days=1)
            elif "today" in q_lower or "aaj" in q_lower or "ajj" in q_lower or "is time" in q_lower or "right now" in q_lower or "abhi" in q_lower or "vartman" in q_lower or "tonight" in q_lower:
                target_date = today

        if target_date:
            offset = (target_date - today).days
            if 0 <= offset <= 14:
                return offset, target_date.strftime("%Y-%m-%d"), False
            elif offset < 0:
                return offset, target_date.strftime("%Y-%m-%d"), False
            else:
                return max(0, min(offset, 14)), target_date.strftime("%Y-%m-%d"), True

        # If follow-up date exists in conversation context
        if last_date:
            try:
                past_dt = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
                offset = (past_dt - today).days
                if 0 <= offset <= 14:
                    return offset, last_date, False
            except Exception:
                pass

        # Default to TODAY (offset 0)
        return 0, today.strftime("%Y-%m-%d"), False

    def parse(
        self,
        query: str,
        last_location: Optional[str] = None,
        last_date: Optional[str] = None
    ) -> Dict[str, Any]:
        norm_q = normalize_query_text(query)
        lang = self.detect_language(norm_q)
        intent_cat = self.classify_intent_category(norm_q)
        intent = self.classify_intent(norm_q)
        loc, state, has_explicit_loc, is_state_query, missing_loc = self.extract_location_and_state(norm_q, last_location)
        offset, date_label, is_out_of_range = self.extract_date_offset(norm_q, last_date)

        # Check for Travel Route (origin & destination)
        travel_origin, travel_dest = None, None
        travel_route_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+se\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', norm_q.lower())
        if not travel_route_match:
            travel_route_match = re.search(r'\bfrom\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+to\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', norm_q.lower())
        if travel_route_match:
            o_cand, d_cand = travel_route_match.group(1).title(), travel_route_match.group(2).title()
            if o_cand.lower() not in NON_LOCATION_STOPWORDS and d_cand.lower() not in NON_LOCATION_STOPWORDS:
                travel_origin = o_cand
                travel_dest = d_cand
                intent_cat = "TRAVEL"
                loc = f"{travel_origin} to {travel_dest}"
                has_explicit_loc = True
                missing_loc = False

        # Check for multiple locations (comparison)
        comparison_locations = []
        multi_loc_match = re.search(r'\b([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\s+(?:aur|and|vs|versus)\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', norm_q.lower())
        if multi_loc_match:
            c1, c2 = multi_loc_match.group(1).title(), multi_loc_match.group(2).title()
            if c1.lower() not in NON_LOCATION_STOPWORDS and c2.lower() not in NON_LOCATION_STOPWORDS:
                comparison_locations = [c1, c2]

        # Follow-up comparison check: "Compare it with Delhi."
        if (intent_cat == "COMPARISON" or "compare" in norm_q.lower()) and len(comparison_locations) < 2 and last_location:
            comp_with_match = re.search(r'\b(?:with|se|aur|and)\s+([a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+)\b', norm_q.lower())
            if comp_with_match:
                cand_comp = comp_with_match.group(1).title()
                if cand_comp.lower() not in NON_LOCATION_STOPWORDS and (cand_comp.lower() in KNOWN_CITIES or cand_comp.lower() in CITY_SYNONYMS or cand_comp.lower() in INDIAN_STATES or cand_comp.lower() in KNOWN_COUNTRIES):
                    comparison_locations = [last_location, cand_comp]
                    intent_cat = "COMPARISON"
                    intent = "comparison"
                    loc = f"{last_location} vs {cand_comp}"
                    has_explicit_loc = True
                    missing_loc = False

        # Check for multiple dates comparison (e.g. Friday and Saturday)
        comparison_dates = []
        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            if re.search(r'\b' + day_name.lower() + r'\b', norm_q.lower()):
                comparison_dates.append(day_name)

        # Check for time of day
        time_of_day = None
        q_low = norm_q.lower()
        if any(w in q_low for w in ["morning", "subah"]):
            time_of_day = "morning"
        elif any(w in q_low for w in ["afternoon", "dopahar"]):
            time_of_day = "afternoon"
        elif any(w in q_low for w in ["evening", "shaam"]):
            time_of_day = "evening"
        elif any(w in q_low for w in ["night", "raat", "tonight"]):
            time_of_day = "night"

        is_historical = (offset < 0 or intent_cat == "HISTORICAL_WEATHER")
        is_continuous_rain = bool(re.search(r'\b(is\s+rain\s+is\s+happening|is\s+rain\s+happening|is\s+it\s+raining|raining\s+now|raining\s+right\s+now|barish\s+ho\s+rahi\s+hai|ho\s+rahi\s+hai)\b', q_low))
        if is_continuous_rain and intent_cat != "RANKING":
            offset = 0
            date_label = "today"
            is_current = True
            intent_cat = "WEATHER_CURRENT"
            intent = "rain"
        else:
            is_current = (offset == 0 and (intent_cat == "WEATHER_CURRENT" or is_continuous_rain or any(w in q_low for w in ["abhi", "vartman", "right now", "current", "is time", "is waqt"])))
        
        # Check for ranking
        ranking_scope = None
        ranking_metric = "rain"
        if intent_cat == "RANKING":
            ranking_scope = loc or "India"
            if any(w in q_low for w in ["temp", "temperature", "tapman", "garmi", "hot", "hottest"]):
                ranking_metric = "temperature_max"
            elif any(w in q_low for w in ["cold", "coldest", "thand", "minimum"]):
                ranking_metric = "temperature_min"
            else:
                ranking_metric = "rain"

        timing_type = None
        is_timing_query = bool(re.search(r'\b(kab\s+hogi|kab\s+hoga|kab\s+aayegi|kab\s+tak|when\s+will|what\s+time|kis\s+samay|kis\s+time|rain\s+kab\s+start|barish\s+kab\s+start|start\s+hone\s+ki\s+possibility)\b', norm_q.lower()))
        if is_timing_query or intent_cat == "RAIN_TIMING":
            is_timing_query = True
            timing_type = "rain"
            intent = "rain_timing"
        elif intent_cat == "OUTDOOR_TIMING" or any(ph in norm_q.lower() for ph in ["barish se bachna", "badhiya time"]):
            is_timing_query = True
            timing_type = "outdoor"
            intent = "outdoor_timing"

        return {
            "query": query,
            "normalized_query": norm_q,
            "detected_language": lang,
            "intent_category": intent_cat,
            "extracted_intent": intent,
            "resolved_location": loc,
            "extracted_state": state,
            "has_explicit_location": has_explicit_loc,
            "is_state_query": is_state_query,
            "missing_location": missing_loc,
            "date_offset": offset,
            "date_label": date_label,
            "is_out_of_range": is_out_of_range,
            "is_historical": is_historical,
            "is_current": is_current,
            "is_timing_query": is_timing_query,
            "timing_type": timing_type,
            "travel_origin": travel_origin,
            "travel_destination": travel_dest,
            "ranking_scope": ranking_scope,
            "ranking_metric": ranking_metric,
            "time_of_day": time_of_day,
            "comparison_locations": comparison_locations,
            "comparison_dates": comparison_dates
        }


nlp_parser = NLPQueryParser()
