import re
import logging
import datetime
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Known global & Indian location names
COMMON_LOCATIONS = [
    "amritsar", "delhi", "new delhi", "mumbai", "bengaluru", "bangalore", "chandigarh",
    "jalandhar", "ludhiana", "patiala", "jaipur", "kolkata", "chennai", "hyderabad",
    "pune", "ahmedabad", "shimla", "srinagar", "lucknow", "varanasi", "agra",
    "london", "tokyo", "new york", "paris", "berlin", "toronto", "sydney", "dubai", "singapore",
    "punjab", "haryana", "uttar pradesh", "maharashtra", "rajasthan", "gujarat", "karnataka",
    "kerala", "tamil nadu", "west bengal", "bihar", "odisha", "assam", "uttarakhand", "himachal pradesh"
]

STATE_ABBREVIATIONS = {
    "up": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",
    "pb": "Punjab",
    "punjab": "Punjab",
    "hr": "Haryana",
    "haryana": "Haryana",
    "dl": "Delhi",
    "uk": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "mp": "Madhya Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "hp": "Himachal Pradesh",
    "himachal pradesh": "Himachal Pradesh",
    "mh": "Maharashtra",
    "maharashtra": "Maharashtra",
    "wb": "West Bengal",
    "west bengal": "West Bengal",
    "tn": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "karnataka": "Karnataka",
    "kl": "Kerala",
    "kerala": "Kerala",
    "ap": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "ts": "Telangana",
    "tg": "Telangana",
    "telangana": "Telangana",
    "rj": "Rajasthan",
    "rajasthan": "Rajasthan",
    "gj": "Gujarat",
    "gujarat": "Gujarat"
}

CITY_SYNONYMS = {
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "bangalore": "Bengaluru",
    "benares": "Varanasi",
    "banaras": "Varanasi",
    "new delhi": "Delhi"
}

ROMAN_PUNJABI_WORDS = {
    "meeh", "pavega", "kida", "rahega", "kina", "hou", "tuhanu", "saade", "pind",
    "da", "dasso", "hovega", "pao", "vekh", "ajj", "kallh", "nu"
}

ROMAN_HINDI_WORDS = {
    "kal", "aaj", "baarish", "barish", "hogi", "hoga", "mausam", "karna", "jaana",
    "chahiye", "hai", "mein", "par", "subah", "shaam", "parso", "parson", "kab", "kya", "ko"
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

NOISE_WORDS = {
    "today", "tomorrow", "yesterday", "day", "after", "morning", "evening", "afternoon", "night",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "september", "august", "july", "june", "october", "november", "december",
    "rain", "temperature", "weather", "forecast", "shower", "wind", "umbrella", "safe", "travel",
    "subah", "shaam", "kal", "aaj", "parso", "parson", "kallh", "ajj", "hogi", "hoga", "pavega",
    "kida", "rahega", "kaisa", "kisi", "will", "what", "how", "is", "it", "the", "like", "tell", "me",
    "mein", "da", "de", "di", "nu", "ka", "ki", "ke", "par", "vich", "hai", "kaisa", "batao", "dasso"
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

    def extract_intent(self, query: str) -> str:
        q_lower = query.lower()

        if any(w in q_lower for w in ["travel", "jaana", "gaddi", "trip", "highway", "drive", "safari"]):
            return "travel"
        elif any(w in q_lower for w in ["spraying", "crop", "kheti", "farmer", "farming", "pesticide", "fertilizer", "kisaan"]):
            return "agriculture"
        elif any(w in q_lower for w in ["event", "wedding", "outdoor", "match", "party", "function", "shaadi"]):
            return "event"
        elif any(w in q_lower for w in ["warning", "alert", "danger", "heavy rain alert", "storm"]):
            return "warning"
        elif any(w in q_lower for w in ["rain", "baarish", "barish", "meeh", "shower", "umbrella"]):
            return "forecast"
        elif any(w in q_lower for w in ["temperature", "garmi", "thand", "temp"]):
            return "forecast"
        return "forecast"

    def extract_location(self, query: str, default_location: str = "Amritsar") -> Tuple[str, bool]:
        """
        Extracts location from user query dynamically.
        Returns (resolved_location, has_explicit_location).
        """
        q_lower = query.lower().strip()
        words = re.findall(r'\b[a-zA-Z\u0900-\u097f\u0a00-\u0a7f]+\b', q_lower)

        # 1. Direct State Abbreviation or City Synonym Lookup
        for word in words:
            if word in STATE_ABBREVIATIONS:
                return STATE_ABBREVIATIONS[word], True
            if word in CITY_SYNONYMS:
                return CITY_SYNONYMS[word], True

        # Check full multi-word state names / city synonyms
        for k, v in STATE_ABBREVIATIONS.items():
            if re.search(r'\b' + re.escape(k) + r'\b', q_lower):
                return v, True
        for k, v in CITY_SYNONYMS.items():
            if re.search(r'\b' + re.escape(k) + r'\b', q_lower):
                return v, True

        # 2. Check exact known locations in query
        for loc in COMMON_LOCATIONS:
            if re.search(r'\b' + re.escape(loc) + r'\b', q_lower):
                return loc.title(), True

        # 3. Regex check for "in <Location>", "for <Location>", "at <Location>", "near <Location>"
        in_match = re.search(r'(?:in|for|at|near)\s+([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)', query, re.IGNORECASE)
        if in_match:
            candidate_words = [w for w in in_match.group(1).split() if w.lower() not in NOISE_WORDS]
            if candidate_words:
                cand_str = " ".join(candidate_words).strip().title()
                if cand_str.lower() in STATE_ABBREVIATIONS:
                    return STATE_ABBREVIATIONS[cand_str.lower()], True
                return cand_str, True

        # 4. Regex check for "<Location> weather/mausam/temperature/forecast"
        weather_match = re.search(r'([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)\s+(?:weather|mausam|temperature|taapman|forecast)', query, re.IGNORECASE)
        if weather_match:
            candidate_words = [w for w in weather_match.group(1).split() if w.lower() not in NOISE_WORDS]
            if candidate_words:
                cand_str = " ".join(candidate_words).strip().title()
                if cand_str.lower() in STATE_ABBREVIATIONS:
                    return STATE_ABBREVIATIONS[cand_str.lower()], True
                return cand_str, True

        # 5. Regex check for Indian languages "<Location> ka/ki/ke/mein/da/de/nu/di/vich"
        lang_post_match = re.search(r'([A-Za-z\u0900-\u097f\u0a00-\u0a7f\s]+)\s+(?:mein|da|de|di|nu|ka|ki|ke|par|vich)', query, re.IGNORECASE)
        if lang_post_match:
            candidate_words = [w for w in lang_post_match.group(1).split() if w.lower() not in NOISE_WORDS]
            if candidate_words:
                cand_str = " ".join(candidate_words).strip().title()
                if cand_str.lower() in STATE_ABBREVIATIONS:
                    return STATE_ABBREVIATIONS[cand_str.lower()], True
                return cand_str, True

        # If no explicit location found in query prompt
        return default_location, False

    def extract_date_offset(self, query: str) -> Tuple[int, str, bool]:
        """
        Returns (days_offset, date_label, is_out_of_range):
        Supports named dates ('15 September', '28 August'), weekdays ('Monday', 'next Sunday'),
        relative day expressions ('kal', 'parso', 'today', 'tomorrow').
        Defaults to offset 0 ("today") when no date is explicitly mentioned.
        """
        today = datetime.date.today()
        q_lower = query.lower()

        # Check numeric date + month, e.g., "15 September", "15 sept", "september 15"
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
            elif "today" in q_lower or "aaj" in q_lower or "ajj" in q_lower:
                target_date = today

        if target_date:
            offset = (target_date - today).days
            if 0 <= offset <= 14:
                return offset, target_date.strftime("%Y-%m-%d"), False
            else:
                return max(0, min(offset, 14)), target_date.strftime("%Y-%m-%d"), True

        # Default to TODAY (offset 0) when user doesn't specify a date horizon
        return 0, today.strftime("%Y-%m-%d"), False

    def parse(self, query: str, default_location: str = "Amritsar") -> Dict[str, Any]:
        lang = self.detect_language(query)
        intent = self.extract_intent(query)
        loc, has_explicit_loc = self.extract_location(query, default_location)
        offset, date_label, is_out_of_range = self.extract_date_offset(query)

        return {
            "query": query,
            "detected_language": lang,
            "extracted_intent": intent,
            "resolved_location": loc,
            "has_explicit_location": has_explicit_loc,
            "date_offset": offset,
            "date_label": date_label,
            "is_out_of_range": is_out_of_range
        }


nlp_parser = NLPQueryParser()

