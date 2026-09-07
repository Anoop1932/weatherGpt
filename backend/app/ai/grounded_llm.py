import os
import logging
import datetime
from typing import Dict, Any, Optional
from app.config import settings
from app.ai.prompts import WEATHERGPT_SYSTEM_PROMPT, GROUNDED_USER_TEMPLATE
from app.schemas.weather_schemas import RiskEvaluation

logger = logging.getLogger(__name__)


class GroundedLLMEngine:

    def generate_non_weather_answer(self, intent: str, lang: str, query: str = "") -> str:
        """
        Generates friendly conversational answers for non-weather queries (greetings, meta, thanks, conversation, gibberish).
        """
        q_low = query.lower() if query else ""

        if intent in ["non_weather_greeting", "greeting"]:
            if lang == "hi":
                return "नमस्ते! 👋 मैं WeatherGPT हूँ। आप मुझसे किसी भी शहर का मौसम, बारिश की संभावना, तापमान या पूर्वाअनुमान पूछ सकते हैं। आप किस स्थान का मौसम जानना चाहते हैं?"
            elif lang == "pa":
                return "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ! 👋 ਮੈਂ WeatherGPT ਹਾਂ। ਮੈਂ ਮੌਸਮ, ਮੀਂਹ, ਤਾਪਮਾਨ ਅਤੇ ਭਵਿੱਖਬਾਣੀ ਵਿੱਚ ਤੁਹਾਡੀ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਤੁਸੀਂ ਕਿਸ ਸ਼ਹਿਰ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਚਾਹੁੰਦੇ ਹੋ?"
            else:
                return "Namaste & Welcome! 👋 I am WeatherGPT, your AI Weather Intelligence Assistant. What weather information would you like to check today?"

        elif intent in ["non_weather_meta", "capability"]:
            if lang == "hi":
                return "Main current weather, forecasts, rain probability, temperature, humidity, wind, alerts aur weather-based advice de sakta hoon — text ya voice se."
            elif lang == "pa":
                return "ਮੈਂ ਮੌਜੂਦਾ ਮੌਸਮ, ਭਵਿੱਖਬਾਣੀ, ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ, ਤਾਪਮਾਨ, ਹਵਾ ਦੀ ਗਤੀ ਅਤੇ ਮੌਸਮ ਸਲਾਹ ਦੇ ਸਕਦਾ ਹਾਂ — ਟੈਕਸਟ ਜਾਂ ਆਵਾਜ਼ ਰਾਹੀਂ।"
            else:
                return "I am WeatherGPT — an AI Weather Intelligence & Decision Assistant. You can ask me about current weather, rain probability, 7-day forecasts, temperature, wind speed, UV index, humidity, or travel and agricultural advisory for any location."

        elif intent in ["non_weather_thanks", "thanks"]:
            if lang == "hi":
                return "आपका स्वागत है! अगर आपको किसी और स्थान का मौसम चेक करना हो, तो बेझिझक पूछें।"
            elif lang == "pa":
                return "ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ! ਜੇਕਰ ਤੁਹਾਨੂੰ ਕਿਸੇ ਹੋਰ ਜਗ੍ਹਾ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਹੋਵੇ ਤਾਂ ਜ਼ਰੂਰ ਦੱਸੋ।"
            else:
                return "You're very welcome! Let me know whenever you need weather updates or forecast information."

        elif intent in ["non_weather_conversation", "social"]:
            if "theek ho" in q_low or "theek" in q_low:
                if lang == "pa":
                    return "ਹਾਂਜੀ 😄 ਮੈਂ ਬਿਲਕੁਲ ਠੀਕ ਹਾਂ! ਦੱਸੋ, ਕਿਸ ਸ਼ਹਿਰ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਹੈ?"
                elif lang == "hi":
                    return "Haan bhai 😄 main bilkul theek hoon! Batao, kis city ka weather dekhna hai?"
                else:
                    return "I'm doing totally fine! 😄 What location's weather would you like to check?"

            if "bhai" in q_low:
                if lang == "pa":
                    return "ਮੈਂ ਵਧੀਆ ਹਾਂ ਵੀਰੇ 😄! ਦੱਸੋ, ਕਿਸ ਸ਼ਹਿਰ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਹੈ?"
                elif lang == "hi":
                    return "Main badhiya hoon bhai 😄 Aap batao, kis city ka weather check karna hai?"
                else:
                    return "Doing great, my friend! 😄 Which city's weather would you like to check?"

            if lang == "hi":
                return "Main badhiya hoon 😄 Aap batao, kis city ka weather check karna hai?"
            elif lang == "pa":
                return "ਮੈਂ ਵਧੀਆ ਹਾਂ 😄! ਦੱਸੋ, ਕਿਸ ਸ਼ਹਿਰ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਹੈ?"
            else:
                return "I'm doing great! 😊 What location would you like me to check?"

        elif intent in ["unclear_gibberish", "unclear"]:
            if lang == "hi":
                return "Sorry, main ye samajh nahi paaya 😅. Aap weather ke baare mein kya jaana chahte hain? Jaise, 'Kal Delhi mein baarish hogi?'"
            elif lang == "pa":
                return "ਮੈਂ ਇਹ ਸਮਝ ਨਹੀਂ ਸਕਿਆ 😅। ਕੀ ਤੁਸੀਂ ਕਿਸੇ ਸ਼ਹਿਰ ਦਾ ਮੌਸਮ ਪੁੱਛਣਾ ਚਾਹੁੰਦੇ ਹੋ? ਜਿਵੇਂ, 'ਕੱਲ੍ਹ ਦਿੱਲੀ ਵਿੱਚ ਮੀਂਹ ਪਵੇਗਾ?'"
            else:
                return "Sorry, I didn't quite understand that 😅. What weather information would you like to check? For example: 'Will it rain in Delhi tomorrow?'"

        return "How can I help you with weather information today?"

    def generate_missing_location_answer(self, lang: str) -> str:
        """
        Generates polite clarification question when user query lacks location and no session context exists.
        """
        if lang == "hi":
            return "बिल्कुल, मैं बता देता हूँ! आप किस शहर या स्थान (city/location) का मौसम चेक करना चाहते हैं?"
        elif lang == "pa":
            return "ਬਿਲਕੁਲ, ਮੈਂ ਦੱਸ ਦਿੰਦਾ ਹਾਂ! ਤੁਸੀਂ ਕਿਸ ਸ਼ਹਿਰ ਜਾਂ ਜਗ੍ਹਾ ਦਾ ਮੌਸਮ ਦੇਖਣਾ ਚਾਹੁੰਦੇ ਹੋ?"
        else:
            return "Sure! Which city or location's weather would you like to check?"

    def generate_grounded_answer(
        self,
        query: str,
        parsed_nlp: Dict[str, Any],
        weather_facts: Dict[str, Any],
        risk_eval: Optional[RiskEvaluation] = None
    ) -> str:
        """
        Synthesizes grounded response using Gemini API or grounded deterministic template fallback.
        """
        lang = parsed_nlp.get("detected_language", "en")
        intent = parsed_nlp.get("extracted_intent", "forecast")

        # Handle non-weather intent
        if intent in ["non_weather_greeting", "non_weather_meta", "non_weather_thanks", "non_weather_conversation", "unclear_gibberish"]:
            return self.generate_non_weather_answer(intent, lang, query=query)

        # Handle missing location
        if parsed_nlp.get("missing_location", False):
            return self.generate_missing_location_answer(lang)

        loc = parsed_nlp.get("resolved_location", "Location")
        date_lbl = parsed_nlp.get("date_label", "today")
        is_out_of_range = parsed_nlp.get("is_out_of_range", False)
        is_state_query = parsed_nlp.get("is_state_query", False)

        if is_out_of_range:
            if lang == "hi":
                return f"**{loc}** के लिए **{date_lbl}** का मौसम पूर्वानुमान अभी उपलब्ध नहीं है। सत्यापित मौसम पूर्वानुमान 14 दिनों की सीमा तक ही उपलब्ध रहता है।"
            elif lang == "pa":
                return f"**{loc}** ਲਈ **{date_lbl}** ਦਾ ਮੌਸਮ ਪੂਰਵ-ਅਨੁਮਾਨ ਹਾਲੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਸਹੀ ਮੌਸਮ ਭਵਿੱਖਬਾਣੀ 14 ਦਿਨਾਂ ਦੀ ਸੀਮਾ ਤੱਕ ਹੀ ਉਪਲਬਧ ਹੈ।"
            else:
                return f"Weather forecast data for **{loc}** on **{date_lbl}** is not currently available. Verified meteorological forecasts extend up to 14 days."

        rain_prob = weather_facts.get("rain_probability", 0)
        temp_max = weather_facts.get("temp_max_c", weather_facts.get("temperature_c", 30.0))
        temp_min = weather_facts.get("temp_min_c", round(temp_max - 6, 1))
        temp_curr = weather_facts.get("temperature_c", temp_max)
        wind_spd = weather_facts.get("max_wind_kmh", weather_facts.get("wind_speed_kmh", 12.0))
        precip_mm = weather_facts.get("precipitation_mm", 0.0)
        humidity = weather_facts.get("humidity", 60.0)
        uv_val = weather_facts.get("uv_index", 5.0)
        vis_km = weather_facts.get("visibility_km", 8.0)
        cond = weather_facts.get("condition_text", "Partly Cloudy")
        source = weather_facts.get("source", "Open-Meteo Meteorological Service")
        updated = weather_facts.get("updated_at", "Just now")
        confidence = weather_facts.get("confidence", "HIGH")
        disagreement = weather_facts.get("disagreement_note") or ""

        # Check Gemini API Key
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

        if api_key and len(api_key) > 5:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                formatted_prompt = GROUNDED_USER_TEMPLATE.format(
                    user_query=query,
                    intent=intent,
                    location=loc,
                    date_horizon=date_lbl,
                    language=lang,
                    forecast_date=weather_facts.get("date", "Today"),
                    temp_max=temp_max,
                    temp_min=temp_min,
                    rain_prob=rain_prob,
                    precip_mm=precip_mm,
                    wind_speed=wind_spd,
                    visibility=vis_km,
                    condition_text=cond,
                    source=source,
                    updated_at=updated,
                    confidence=confidence,
                    disagreement_note=disagreement,
                    risk_level=risk_eval.risk_level if risk_eval else "LOW",
                    category=risk_eval.category if risk_eval else "general",
                    reasons=", ".join(risk_eval.reasons) if risk_eval else "Normal weather",
                    recommendation=risk_eval.recommendation if risk_eval else "No special advisories."
                )

                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=formatted_prompt,
                    config={"system_instruction": WEATHERGPT_SYSTEM_PROMPT}
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.warning(f"Gemini API call failed ({e}). Falling back to grounded template synthesizer.")

        # Grounded Deterministic Template Fallback (100% Dynamic & Conversational)
        return self._generate_fallback_answer(
            query=query,
            lang=lang,
            loc=loc,
            date_lbl=date_lbl,
            intent=intent,
            temp_max=temp_max,
            temp_min=temp_min,
            temp_curr=temp_curr,
            rain_prob=rain_prob,
            precip_mm=precip_mm,
            wind_spd=wind_spd,
            humidity=humidity,
            uv_val=uv_val,
            vis_km=vis_km,
            cond=cond,
            risk_eval=risk_eval,
            is_state_query=is_state_query,
            source=source,
            updated=updated,
            confidence=confidence,
            disagreement=disagreement
        )

    def _generate_fallback_answer(
        self,
        query: str,
        lang: str,
        loc: str,
        date_lbl: str,
        intent: str,
        temp_max: float,
        temp_min: float,
        temp_curr: float,
        rain_prob: float,
        precip_mm: float,
        wind_spd: float,
        humidity: float,
        uv_val: float,
        vis_km: float,
        cond: str,
        risk_eval: Optional[RiskEvaluation],
        is_state_query: bool,
        source: str,
        updated: str,
        confidence: str,
        disagreement: str
    ) -> str:
        
        hi_cond = {
            "Clear Sky": "साफ मौसम",
            "Mainly Clear": "मुख्यतः साफ मौसम",
            "Partly Cloudy": "आंशिक रूप से बादल",
            "Overcast": "छाए हुए बादल",
            "Foggy": "कोहरा",
            "Light Drizzle": "हल्की बूंदाबांदी",
            "Moderate Rain": "मध्यम बारिश",
            "Heavy Rain": "भारी बारिश",
            "Slight Rain Showers": "बारिश की बौछारें",
            "Thunderstorm": "गरज के साथ तूफान"
        }.get(cond, cond)

        prefix = ""
        if is_state_query:
            if lang == "hi":
                prefix = f"*{loc} एक बड़ा राज्य है, इसलिए अलग-अलग शहरों में मौसम भिन्न हो सकता है। राज्य का औसतन पूर्वानुमान:*\n\n"
            elif lang == "pa":
                prefix = f"*{loc} ਇੱਕ ਵੱਡਾ ਰਾਜ ਹੈ, ਇਸ ਲਈ ਮੌਸਮ ਸ਼ਹਿਰ ਦੇ ਹਿਸਾਬ ਨਾਲ ਵੱਖਰਾ ਹੋ ਸਕਦਾ ਹੈ। ਖੇਤਰੀ ਅਨੁਮਾਨ:*\n\n"
            else:
                prefix = f"*{loc} is a large region, so weather varies by city. Regional baseline forecast:*\n\n"

        today_str = datetime.date.today().strftime("%Y-%m-%d")

        if lang == "hi":
            date_str = "आज" if "today" in date_lbl.lower() or date_lbl == today_str else ("कल" if "tomorrow" in date_lbl.lower() else date_lbl)
            
            if intent == "rain":
                if rain_prob > 40:
                    ans = prefix + f"हाँ, {date_str} **{loc}** में बारिश की संभावना लगभग **{rain_prob}%** है (अनुमानित वर्षा: {precip_mm} मिमी)। अधिकतम तापमान करीब **{temp_max}°C** रहेगा और मौसम {hi_cond} रहेगा।"
                else:
                    ans = prefix + f"{date_str} **{loc}** में बारिश की संभावना काफी कम है — केवल **{rain_prob}%**। मौसम मुख्यतः **{hi_cond}** और अधिकतम तापमान **{temp_max}°C** रहेगा।"
            
            elif intent == "temperature":
                ans = prefix + f"{date_str} **{loc}** में अधिकतम तापमान **{temp_max}°C** और न्यूनतम तापमान **{temp_min}°C** रहने का अनुमान है। मौसम **{hi_cond}** रहेगा।"
            
            elif intent == "humidity":
                ans = prefix + f"**{loc}** में आर्द्रता (humidity) का स्तर **{humidity}%** है। तापमान **{temp_curr}°C** है।"
            
            elif intent == "wind":
                ans = prefix + f"**{loc}** में हवा की गति लगभग **{wind_spd} किमी/घंटा** है।"
            
            elif intent == "uv":
                ans = prefix + f"**{loc}** में अधिकतम UV Index **{uv_val}** रहेगा।"
            
            elif intent == "visibility":
                ans = prefix + f"**{loc}** में दृश्यता (visibility) लगभग **{vis_km} किमी** है। मौसम **{hi_cond}** है।"
            
            elif intent == "current_weather":
                ans = prefix + f"**{loc}** में इस समय वर्तमान तापमान **{temp_curr}°C** है, मौसम **{hi_cond}** है, हवा की गति **{wind_spd} किमी/घंटा** और बारिश की संभावना **{rain_prob}%** है।"

            elif intent == "outdoor_activity":
                if rain_prob > 40:
                    ans = prefix + f"{date_str} **{loc}** में बाहरी गतिविधियों (outdoor events) के लिए बारिश खलल डाल सकती है। बारिश की संभावना **{rain_prob}%** है और अधिकतम तापमान **{temp_max}°C** रहेगा।"
                else:
                    ans = prefix + f"हाँ! {date_str} **{loc}** में बाहरी कार्यक्रमों (outdoor events) के लिए मौसम अनुकूल रहेगा। बारिश की संभावना काफी कम (**{rain_prob}%**) है और तापमान लगभग **{temp_max}°C** रहेगा ({hi_cond})।"

            elif intent == "agriculture":
                if rain_prob > 40 or wind_spd > 25:
                    ans = prefix + f"{date_str} **{loc}** में छिड़काव (spraying/farming) की सलाह नहीं दी जाती है क्योंकि बारिश की संभावना **{rain_prob}%** और हवा की गति **{wind_spd} किमी/घंटा** है।"
                else:
                    ans = prefix + f"हाँ, {date_str} **{loc}** में फसलों पर कीटनाशक/उर्वरक छिड़काव के लिए मौसम अनुकूल है। बारिश की संभावना केवल **{rain_prob}%** और हवा शांत ({wind_spd} किमी/घंटा) है।"

            else:
                ans = prefix + f"{date_str} **{loc}** में बारिश की संभावना **{rain_prob}%** है। अधिकतम तापमान **{temp_max}°C** और न्यूनतम **{temp_min}°C** रहने का अनुमान है ({hi_cond})।"

            if risk_eval and risk_eval.risk_level in ["MODERATE", "HIGH", "SEVERE"]:
                ans += f"\n\n**जोखिम स्तर ({risk_eval.risk_level}):** {risk_eval.recommendation}"

            return ans

        elif lang == "pa":
            date_str = "ਅੱਜ" if "today" in date_lbl.lower() or date_lbl == today_str else ("ਕੱਲ੍ਹ" if "tomorrow" in date_lbl.lower() else date_lbl)

            if intent == "rain":
                if rain_prob > 40:
                    ans = prefix + f"ਹਾਂ, {date_str} **{loc}** ਵਿੱਚ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਲਗਭਗ **{rain_prob}%** ਹੈ (ਅਨੁਮਾਨਿਤ ਵਰਖਾ: {precip_mm} ਮਿਲੀਮੀਟਰ)। ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ।"
                else:
                    ans = prefix + f"{date_str} **{loc}** ਵਿੱਚ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਕਾਫ਼ੀ ਘੱਟ ਹੈ — ਸਿਰਫ਼ **{rain_prob}%**। ਮੌਸਮ **{cond}** ਅਤੇ ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ।"
            
            elif intent == "outdoor_activity":
                if rain_prob > 40:
                    ans = prefix + f"{date_str} **{loc}** ਵਿੱਚ ਬਾਹਰੀ ਸਮਾਗਮਾਂ ਲਈ ਮੀਂਹ ਪੈਣ ਦੀ ਸੰਭਾਵਨਾ (**{rain_prob}%**) ਹੈ। ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ।"
                else:
                    ans = prefix + f"ਹਾਂ! {date_str} **{loc}** ਵਿੱਚ ਬਾਹਰੀ ਪ੍ਰੋਗਰਾਮਾਂ (outdoor events) ਲਈ ਮੌਸਮ ਵਧੀਆ ਰਹੇਗਾ। ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਸਿਰਫ਼ **{rain_prob}%** ਹੈ ਅਤੇ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ।"

            elif intent == "agriculture":
                if rain_prob > 40 or wind_spd > 25:
                    ans = prefix + f"{date_str} **{loc}** ਵਿੱਚ ਸਪਰੇਅ ਕਰਨ ਲਈ ਮੌਸਮ ਅਨੁਕੂਲ ਨਹੀਂ ਹੈ (ਮੀਂਹ: {rain_prob}%, ਹਵਾ: {wind_spd} ਕਿਮੀ/ਘੰਟਾ)।"
                else:
                    ans = prefix + f"ਹਾਂ, {date_str} **{loc}** ਵਿੱਚ ਫ਼ਸਲਾਂ 'ਤੇ ਸਪਰੇਅ ਕਰਨ ਲਈ ਮੌਸਮ ਵਧੀਆ ਹੈ। ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਸਿਰਫ਼ {rain_prob}% ਹੈ।"

            elif intent == "temperature":
                ans = prefix + f"{date_str} **{loc}** ਵਿੱਚ ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਅਤੇ ਘੱਟ ਤੋਂ ਘੱਟ ਤਾਪਮਾਨ **{temp_min}°C** ਰਹਿਣ ਦਾ ਅਨੁਮਾਨ ਹੈ।"

            elif intent == "current_weather":
                ans = prefix + f"**{loc}** ਵਿੱਚ ਇਸ ਸਮੇਂ ਤਾਪਮਾਨ **{temp_curr}°C** ਹੈ, ਮੌਸਮ **{cond}** ਹੈ ਅਤੇ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ **{rain_prob}%** ਹੈ।"

            else:
                ans = prefix + f"{date_str} **{loc}** ਵਿੱਚ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ **{rain_prob}%** ਹੈ। ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ ({cond})।"

            if risk_eval and risk_eval.risk_level in ["MODERATE", "HIGH", "SEVERE"]:
                ans += f"\n\n**ਜੋਖਮ ਪੱਧਰ ({risk_eval.risk_level}):** {risk_eval.recommendation}"

            return ans

        else:
            # English response
            date_str = "today" if "today" in date_lbl.lower() or date_lbl == today_str else ("tomorrow" if "tomorrow" in date_lbl.lower() else f"on {date_lbl}")

            if intent == "rain":
                if rain_prob > 40:
                    ans = prefix + f"Yes, there is a high **{rain_prob}%** chance of rain in **{loc}** {date_str} with estimated precipitation of **{precip_mm}mm**. Max temperature will reach **{temp_max}°C**."
                else:
                    ans = prefix + f"Rain probability in **{loc}** {date_str} is low — approx **{rain_prob}%**. Weather will be mostly **{cond}** with maximum temperature around **{temp_max}°C**."

            elif intent == "outdoor_activity":
                if rain_prob > 40 or precip_mm > 2.0:
                    ans = prefix + f"Outdoor activities in **{loc}** {date_str} may be affected by rain. Rain probability is **{rain_prob}%** ({precip_mm}mm precipitation expected) with maximum temperature around **{temp_max}°C**."
                else:
                    ans = prefix + f"Yes! Weather conditions in **{loc}** {date_str} look good for outdoor events. Rain probability is low (**{rain_prob}%**), with expected max temperature around **{temp_max}°C** and **{cond}** conditions."

            elif intent == "agriculture":
                if rain_prob > 40 or wind_spd > 25:
                    ans = prefix + f"Farming and spraying operations in **{loc}** {date_str} are not recommended. Rain probability is **{rain_prob}%** and wind speed is **{wind_spd} km/h**."
                else:
                    ans = prefix + f"Yes, weather conditions in **{loc}** {date_str} are suitable for farming and spraying. Rain probability is low (**{rain_prob}%**) with calm winds at **{wind_spd} km/h** ({cond})."

            elif intent == "temperature":
                ans = prefix + f"In **{loc}** {date_str}, expected maximum temperature is **{temp_max}°C** and minimum temperature is **{temp_min}°C** ({cond})."

            elif intent == "humidity":
                ans = prefix + f"Relative humidity in **{loc}** is **{humidity}%** with current temperature at **{temp_curr}°C**."

            elif intent == "wind":
                ans = prefix + f"Wind speed in **{loc}** is approximately **{wind_spd} km/h**."

            elif intent == "current_weather":
                ans = prefix + f"Current weather in **{loc}** is **{temp_curr}°C** ({cond}), rain probability is **{rain_prob}%**, and wind speed is **{wind_spd} km/h**."

            else:
                ans = prefix + f"In **{loc}** ({date_str}), rain probability is **{rain_prob}%** with expected max temperature of **{temp_max}°C** ({cond})."

            if risk_eval and risk_eval.risk_level in ["MODERATE", "HIGH", "SEVERE"]:
                ans += f"\n\n**Risk Level ({risk_eval.risk_level}):** {risk_eval.recommendation}"

            return ans


grounded_llm_engine = GroundedLLMEngine()
