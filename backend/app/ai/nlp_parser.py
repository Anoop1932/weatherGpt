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
    "assam": "Assam", "as": "Assam",
    "jharkhand": "Jharkhand", "jh": "Jharkhand",
    "chhattisgarh": "Chhattisgarh", "cg": "Chhattisgarh", "ch": "Chhattisgarh",
    "goa": "Goa", "ga": "Goa",
    "jammu and kashmir": "Jammu & Kashmir", "jk": "Jammu & Kashmir", "j&k": "Jammu & Kashmir",
    "ladakh": "Ladakh",
    "chandigarh": "Chandigarh", "chd": "Chandigarh"
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
    "vizag": "Visakhapatnam"
}

ROMAN_PUNJABI_WORDS = {
    "meeh", "pavega", "kida", "rahega", "kina", "hou", "tuhanu", "saade", "pind",
    "da", "dasso", "hovega", "pao", "vekh", "ajj", "kallh", "nu", "vich", "ki aa", "kaisa aa"
}

ROMAN_HINDI_WORDS = {
    "kal", "aaj", "baarish", "barish", "hogi", "hoga", "mausam", "karna", "jaana",
    "chahiye", "hai", "mein", "par", "subah", "shaam", "parso", "parson", "kab", "kya", "ko",
    "kitni", "kitna", "kaisa", "batao", "bata"
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
    "good", "bad", "best", "better", "suitable", "likely", "possible", "safe", "unsafe",
    "great", "fine", "nice", "pleasant", "harsh", "extreme", "severe", "perfect",
    # Activity & Event Words
    "outdoor", "indoors", "indoor", "events", "event", "activity", "activities", "picnic",
    "travel", "trip", "journey", "tour", "drive", "farming", "farm", "crops", "spraying",
    "match", "party", "wedding", "shaadi", "function", "outing", "walk", "jog", "outside",
    # Weather Vocabulary
    "weather", "forecast", "mausam", "taapman", "temperature", "rain", "barish", "baarish",
    "meeh", "shower", "drizzle", "sun", "sunny", "cloud", "cloudy", "wind", "windy", "hawa",
    "storm", "stormy", "fog", "foggy", "dhund", "humidity", "nami", "uv", "visibility", "pressure",
    # Time Vocabulary
    "today", "tomorrow", "yesterday", "day", "after", "morning", "evening", "afternoon", "night",
    "tonight", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august", "september",
    "october", "november", "december", "subah", "shaam", "kal", "aaj", "parso", "parson",
    "kallh", "ajj", "is time", "time", "current", "right now", "now", "abhi", "waqt",
    # Auxiliary, Prepositions & Question Connectors
    "is", "are", "am", "was", "were", "be", "been", "being", "will", "would", "could", "should",
    "can", "may", "might", "must", "do", "does", "did", "have", "has", "had",
    "in", "at", "near", "around", "for", "from", "to", "by", "with", "on", "of", "the", "a", "an", "s", "about",
    # Questions & Pronouns
    "what", "when", "where", "how", "why", "who", "which", "it", "you", "me", "i",
    "we", "us", "they", "them", "my", "your", "our", "their", "this", "that", "there", "here",
    # Additional Noise & Request Words
    "probability", "chance", "chances", "possibility", "level", "status", "condition", "conditions",
    "tell", "show", "give", "check", "info", "information", "details", "report", "update", "updates", "stats",
    # Hindi / Hinglish / Punjabi Noise
    "mein", "da", "de", "di", "nu", "ka", "ki", "ke", "par", "vich", "hai", "batao", "dasso",
    "kya", "ko", "kya hai", "hein", "hain", "kitni", "kitna", "kab", "kaisa", "kisi", "sahi",
    "rahega", "hoga", "hogi", "pavega", "hovega", "kida", "kiska", "kaha", "kahan", "sakta",
    "hun", "hu", "main", "tum", "aap", "tusi", "kar", "karna", "karne", "bata", "dikhaye", "dikhao",
    "carry", "umbrella", "take", "bring", "go", "going"
}


class NLPQueryParser:

    def detect_language(self, query: str) -> str:
        """
        Detects message language:
        - Gurmukhi script or Roman Punjabi -> 'pa'
        - Devanagari script or Roman Hindi / Hinglish -> 'hi'
        - English -> 'en'
        """
        if re.search(r'[\u0A00-\u0A7F]', query):
            return "pa"

        if re.search(r'[\u0900-\u097F]', query):
            return "hi"

        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        if len(query_words.intersection(ROMAN_PUNJABI_WORDS)) >= 1:
            return "pa"

        if len(query_words.intersection(ROMAN_HINDI_WORDS)) >= 1:
            return "hi"

        return "en"

    def classify_intent(self, query: str) -> str:
        """
        Classifies intent into weather parameters, activities, or non-weather categories:
        - non_weather_greeting
        - non_weather_meta
        - non_weather_thanks
        - outdoor_activity
        - rain / precipitation
        - temperature
        - humidity
        - wind
        - uv
        - visibility
        - pressure
        - sunrise_sunset
        - current_weather
        - travel / agriculture / event / warning / forecast
        """
        q_lower = query.lower().strip()

        # 1. Non-weather Greetings
        if re.search(r'\b(hello|hi|hey|namaste|namaskar|sat sri akal|pranam| प्रणाम|प्रणाम)\b', q_lower) and not any(w in q_lower for w in ["weather", "barish", "rain", "mausam", "temp"]):
            return "non_weather_greeting"

        # 2. Non-weather Meta / Capabilities / Identity
        if any(ph in q_lower for ph in ["who are you", "who r u", "tum kaun ho", "aap kaun ho", "tusi kaun ho", "what can you do", "main kya kar sakta", "kya kar sakte ho", "help me"]):
            return "non_weather_meta"

        # 3. Non-weather Thanks
        if re.search(r'\b(thank you|thanks|shukriya|dhanyawad|dhanwad|thanku)\b', q_lower):
            return "non_weather_thanks"

        # 4. Outdoor Activities & Outdoor Events
        if any(w in q_lower for w in ["outdoor", "outdoors", "events", "event", "picnic", "go outside", "outside", "activities", "outing"]):
            return "outdoor_activity"

        # 5. Domain Specific Intents
        if any(w in q_lower for w in ["travel", "jaana", "gaddi", "trip", "highway", "drive", "safari"]):
            return "travel"
        elif any(w in q_lower for w in ["spraying", "crop", "kheti", "farmer", "farming", "pesticide", "fertilizer", "kisaan"]):
            return "agriculture"
        elif any(w in q_lower for w in ["wedding", "match", "party", "function", "shaadi"]):
            return "event"
        elif any(w in q_lower for w in ["warning", "alert", "danger", "heavy rain alert", "storm"]):
            return "warning"

        # 6. Weather Specific Parameters
        if any(w in q_lower for w in ["rain", "baarish", "barish", "meeh", "shower", "drizzle", "barish hogi", "meeh pavega", "umbrella"]):
            return "rain"
        elif any(w in q_lower for w in ["temperature", "tapman", "taapman", "garmi", "thand", "temp", "hot", "cold"]):
            return "temperature"
        elif any(w in q_lower for w in ["humidity", "nami", "kitni"]):
            return "humidity"
        elif any(w in q_lower for w in ["wind", "hawa", "tez hawa", "breeze"]):
            return "wind"
        elif any(w in q_lower for w in ["uv", "uv index", "dhoop", "sunlight"]):
            return "uv"
        elif any(w in q_lower for w in ["visibility", "dhund", "fog", "smog"]):
            return "visibility"
        elif any(w in q_lower for w in ["pressure"]):
            return "pressure"
        elif any(w in q_lower for w in ["sunrise", "sunset", "suraj"]):
            return "sunrise_sunset"
        elif any(w in q_lower for w in ["is time", "right now", "current", "abhi", "is waqt"]):
            return "current_weather"

        return "forecast"

    def extract_location_and_state(
        self,
        query: str,
        last_location: Optional[str] = None
    ) -> Tuple[str, Optional[str], bool, bool, bool]:
        """
        Extracts location & state dynamically from user query using prepositions, stopwords & state recognition.
        Returns:
        (resolved_location, extracted_state, has_explicit_location, is_state_query, missing_location)
        """
        q_lower = re.sub(r"'s\b", "", query.lower().strip())
        
        extracted_state = None

        # Check for explicit state mention in query
        for state_key, state_canonical in INDIAN_STATES.items():
            if re.search(r'\b' + re.escape(state_key) + r'\b', q_lower):
                extracted_state = state_canonical
                break

        # Check for city synonyms
        for syn_key, syn_canonical in CITY_SYNONYMS.items():
            if re.search(r'\b' + re.escape(syn_key) + r'\b', q_lower):
                return syn_canonical, extracted_state, True, False, False

        # 1. Preposition Location Signals (English & Hindi/Punjabi)
        # e.g., "in Amritsar", "at Jalandhar", "near Kapurthala", "for Delhi", "around Chandigarh"
        prep_match = re.search(r'\b(?:in|at|near|around|from|for)\s+([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)', q_lower)
        if prep_match:
            candidate_raw = prep_match.group(1).strip()
            prep_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', candidate_raw) if w.lower() not in NON_LOCATION_STOPWORDS]
            if prep_words:
                place_name = " ".join(prep_words)
                # Check if place_name matches state name
                if place_name.lower() in INDIAN_STATES:
                    st_name = INDIAN_STATES[place_name.lower()]
                    return st_name, st_name, True, True, False
                if extracted_state and place_name.lower() != extracted_state.lower():
                    return f"{place_name}, {extracted_state}", extracted_state, True, False, False
                return place_name, extracted_state, True, False, False

        # Hindi/Punjabi postpositions e.g. "Amritsar mein", "Patna vich", "Jalandhar da"
        post_match = re.search(r'([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)\s+(?:mein|vich|da|de|di|nu|ka|ki|ke|par)\b', q_lower)
        if post_match:
            candidate_raw = post_match.group(1).strip()
            post_words = [w.title() for w in re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', candidate_raw) if w.lower() not in NON_LOCATION_STOPWORDS]
            if post_words:
                place_name = " ".join(post_words)
                if place_name.lower() in INDIAN_STATES:
                    st_name = INDIAN_STATES[place_name.lower()]
                    return st_name, st_name, True, True, False
                if extracted_state and place_name.lower() != extracted_state.lower():
                    return f"{place_name}, {extracted_state}", extracted_state, True, False, False
                return place_name, extracted_state, True, False, False

        # 2. General Token Filter (strictly excluding NON_LOCATION_STOPWORDS)
        words = re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', q_lower)
        candidate_words = []
        for word in words:
            w_clean = word.lower()
            if w_clean in NON_LOCATION_STOPWORDS:
                continue
            if extracted_state and (w_clean == extracted_state.lower() or w_clean in INDIAN_STATES):
                continue
            candidate_words.append(word.title())

        # If candidate place words exist
        if candidate_words:
            place_name = " ".join(candidate_words)
            if extracted_state and place_name.lower() != extracted_state.lower():
                return f"{place_name}, {extracted_state}", extracted_state, True, False, False
            return place_name, extracted_state, True, False, False

        # If no city name, but an explicit state was mentioned (e.g., "Punjab ka weather")
        if extracted_state:
            return extracted_state, extracted_state, True, True, False

        # If no explicit location in query, use conversation session context if available
        if last_location and last_location.strip():
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
        today = datetime.date.today()
        q_lower = query.lower()

        # Check for numeric date + month, e.g., "15 September", "september 15"
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
            if "day after tomorrow" in q_lower or "parson" in q_lower or "parso" in q_lower:
                target_date = today + datetime.timedelta(days=2)
            elif "tomorrow" in q_lower or "kal" in q_lower or "kallh" in q_lower:
                target_date = today + datetime.timedelta(days=1)
            elif "today" in q_lower or "aaj" in q_lower or "ajj" in q_lower or "is time" in q_lower or "right now" in q_lower or "abhi" in q_lower or "tonight" in q_lower:
                target_date = today

        if target_date:
            offset = (target_date - today).days
            if 0 <= offset <= 14:
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
        lang = self.detect_language(query)
        intent = self.classify_intent(query)
        loc, state, has_explicit_loc, is_state_query, missing_loc = self.extract_location_and_state(query, last_location)
        offset, date_label, is_out_of_range = self.extract_date_offset(query, last_date)

        return {
            "query": query,
            "detected_language": lang,
            "extracted_intent": intent,
            "resolved_location": loc,
            "extracted_state": state,
            "has_explicit_location": has_explicit_loc,
            "is_state_query": is_state_query,
            "missing_location": missing_loc,
            "date_offset": offset,
            "date_label": date_label,
            "is_out_of_range": is_out_of_range
        }


nlp_parser = NLPQueryParser()
