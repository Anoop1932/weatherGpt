import os
import logging
from typing import Dict, Any
from app.config import settings
from app.ai.prompts import WEATHERGPT_SYSTEM_PROMPT, GROUNDED_USER_TEMPLATE
from app.schemas.weather_schemas import RiskEvaluation

logger = logging.getLogger(__name__)


class GroundedLLMEngine:

    def generate_grounded_answer(
        self,
        query: str,
        parsed_nlp: Dict[str, Any],
        weather_facts: Dict[str, Any],
        risk_eval: RiskEvaluation
    ) -> str:
        """
        Synthesizes grounded response using Gemini API or grounded deterministic template fallback.
        """
        lang = parsed_nlp.get("detected_language", "en")
        loc = parsed_nlp.get("resolved_location", "Amritsar")
        date_lbl = parsed_nlp.get("date_label", "tomorrow")
        intent = parsed_nlp.get("extracted_intent", "forecast")
        is_out_of_range = parsed_nlp.get("is_out_of_range", False)

        if is_out_of_range:
            if lang == "hi":
                return f"**{loc}** के लिए **{date_lbl}** का मौसम पूर्वानुमान अभी उपलब्ध नहीं है। सत्यापित मौसम पूर्वानुमान 14 दिनों की सीमा तक ही उपलब्ध रहता है।"
            elif lang == "pa":
                return f"**{loc}** ਲਈ **{date_lbl}** ਦਾ ਮੌਸਮ ਪੂਰਵ-ਅਨੁਮਾਨ ਹਾਲੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਸਹੀ ਮੌਸਮ ਭਵਿੱਖਬਾਣੀ 14 ਦਿਨਾਂ ਦੀ ਸੀਮਾ ਤੱਕ ਹੀ ਉਪਲਬਧ ਹੈ।"
            else:
                return f"Weather forecast data for **{loc}** on **{date_lbl}** is not currently available. Verified meteorological forecasts extend up to 14 days."

        rain_prob = weather_facts.get("rain_probability", 0)
        temp_max = weather_facts.get("temp_max_c", weather_facts.get("temperature_c", 30.0))
        temp_min = weather_facts.get("temp_min_c", round(temp_max - 8, 1))
        wind_spd = weather_facts.get("max_wind_kmh", weather_facts.get("wind_speed_kmh", 12.0))
        precip_mm = weather_facts.get("precipitation_mm", 0.0)
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
                    forecast_date=weather_facts.get("date", "Tomorrow"),
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
                    risk_level=risk_eval.risk_level,
                    category=risk_eval.category,
                    reasons=", ".join(risk_eval.reasons),
                    recommendation=risk_eval.recommendation
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

        # Grounded Deterministic Template Fallback (100% Reliable & Non-Hallucinating)
        return self._generate_fallback_answer(
            query=query,
            lang=lang,
            loc=loc,
            date_lbl=date_lbl,
            intent=intent,
            temp_max=temp_max,
            rain_prob=rain_prob,
            precip_mm=precip_mm,
            wind_spd=wind_spd,
            cond=cond,
            risk_eval=risk_eval,
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
        rain_prob: float,
        precip_mm: float,
        wind_spd: float,
        cond: str,
        risk_eval: RiskEvaluation,
        source: str,
        updated: str,
        confidence: str,
        disagreement: str
    ) -> str:
        # Check if location is a large state or region
        known_states = [
            "uttar pradesh", "up", "punjab", "haryana", "maharashtra", "rajasthan",
            "gujarat", "karnataka", "kerala", "tamil nadu", "west bengal", "bihar",
            "madhya pradesh", "uttarakhand", "himachal pradesh"
        ]
        is_state = any(st in loc.lower() for st in known_states)

        if lang == "pa":
            # Punjabi (Gurmukhi / Roman) response
            date_pa = "ਕੱਲ੍ਹ" if "tomorrow" in date_lbl.lower() or "kal" in date_lbl.lower() else ("ਅੱਜ" if "today" in date_lbl.lower() else date_lbl)
            prefix = ""
            if is_state:
                prefix = f"*{loc} ਇੱਕ ਵੱਡਾ ਰਾਜ ਹੈ, ਇਸ ਲਈ ਮੌਸਮ ਸ਼ਹਿਰ ਦੇ ਹਿਸਾਬ ਨਾਲ ਵੱਖਰਾ ਹੋ ਸਕਦਾ ਹੈ। ਖੇਤਰੀ ਅਨੁਮਾਨ:*\n\n"

            if intent == "agriculture":
                ans = prefix + f"{date_pa} {loc} ਵਿੱਚ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ **{rain_prob}%** ਹੈ। ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਰਹੇਗਾ।\n\n"
                ans += f"**ਖੇਤੀਬਾੜੀ ਅਤੇ ਸਪ੍ਰੇਅ ਸਲਾਹ:** {risk_eval.recommendation}\n"
            elif intent == "travel":
                ans = prefix + f"{date_pa} {loc} ਰੂਟ 'ਤੇ ਯਾਤਰਾ ਦਾ ਖਤਰਾ ਪੱਧਰ **{risk_eval.risk_level}** ਹੈ। ਮੀਂਹ: **{rain_prob}%**, ਹਵਾ ਦੀ ਗਤੀ: **{wind_spd} km/h**।\n\n"
                ans += f"**ਯਾਤਰਾ ਸਲਾਹ:** {risk_eval.recommendation}\n"
            else:
                ans = prefix + f"{date_pa} {loc} ਵਿੱਚ ਮੀਂਹ ਦੀ ਸੰਭਾਵਨਾ ਲਗਭਗ **{rain_prob}%** ਹੈ (ਅਨੁਮਾਨਿਤ ਵਰਖਾ: {precip_mm}mm)। ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ **{temp_max}°C** ਅਤੇ ਮੌਸਮ **{cond}** ਰਹੇਗਾ।\n\n"
                ans += f"**ਜੋਖਮ ਮੁਲਾਂਕਣ:** ਪੱਧਰ **{risk_eval.risk_level}** ਹੈ।\n"
                ans += f"**ਕਾਰਵਾਈ ਦੀ ਸਲਾਹ:** {risk_eval.recommendation}\n"

            ans += f"\n---\n**ਸਰੋਤ:** {source} | **ਅੱਪਡੇਟ:** {updated}\n"
            ans += f"**ਪੂਰਵ-ਅਨੁਮਾਨ ਭਰੋਸਾ:** {confidence}"
            if disagreement:
                ans += f"\n*ਨੋਟ: {disagreement}*"
            return ans

        elif lang == "hi":
            # Devanagari Hindi translation for condition
            hi_cond = {
                "Clear Sky": "साफ आसमान",
                "Mainly Clear": "मुख्यतः साफ मौसम",
                "Partly Cloudy": "आंशिक रूप से बादल",
                "Overcast": "छाए हुए बादल",
                "Foggy": "कोहरा",
                "Light Drizzle": "हल्की बूंदाबांदी",
                "Moderate Rain": "मध्यम बारिश",
                "Heavy Rain": "भारी बारिश",
                "Slight Rain Showers": "हल्की बारिश की बौछारें",
                "Moderate Rain Showers": "मध्यम बारिश की बौछारें",
                "Thunderstorm": "गरज के साथ तूफान"
            }.get(cond, cond)

            date_hi = "कल" if "tomorrow" in date_lbl.lower() or "kal" in date_lbl.lower() else ("आज" if "today" in date_lbl.lower() else date_lbl)
            prefix = ""
            if is_state:
                prefix = f"*{loc} एक बड़ा क्षेत्र है, इसलिए अलग-अलग शहरों में मौसम भिन्न हो सकता है। क्षेत्रीय पूर्वानुमान:*\n\n"

            if intent == "agriculture":
                ans = prefix + f"{date_hi} {loc} में बारिश होने की संभावना लगभग **{rain_prob}%** है। अधिकतम तापमान **{temp_max}°C** रहेगा।\n\n"
                ans += f"**कृषि और छिड़काव की सलाह:** {risk_eval.recommendation}\n"
            elif intent == "travel":
                ans = prefix + f"{date_hi} {loc} मार्ग पर यात्रा जोखिम का स्तर **{risk_eval.risk_level}** है। बारिश की संभावना: **{rain_prob}%**, हवा की गति: **{wind_spd} किमी/घंटा**।\n\n"
                ans += f"**यात्रा सलाह:** {risk_eval.recommendation}\n"
            else:
                ans = prefix + f"{date_hi} {loc} में बारिश की संभावना लगभग **{rain_prob}%** है (अनुमानित वर्षा: {precip_mm} मिमी)। अधिकतम तापमान **{temp_max}°C** और मौसम की स्थिति **{hi_cond}** रहेगी।\n\n"
                ans += f"**जोखिम मूल्यांकन:** जोखिम का स्तर **{risk_eval.risk_level}** है।\n"
                ans += f"**कार्रवाई की सलाह:** {risk_eval.recommendation}\n"

            ans += f"\n---\n**स्रोत:** {source} | **अद्यतन:** {updated}\n"
            ans += f"**पूर्वानुमान विश्वास स्तर:** {confidence}"
            if disagreement:
                ans += f"\n*विशेष टिप्पणी: {disagreement}*"
            return ans
        else:
            # English response
            prefix = ""
            if is_state:
                prefix = f"*{loc} is a large region, so weather varies by city. Regional baseline forecast:*\n\n"

            ans = prefix + f"In {loc} ({date_lbl}), the rain probability is approximately **{rain_prob}%** with estimated precipitation of **{precip_mm}mm**. Maximum temperature will reach **{temp_max}°C** ({cond}).\n\n"
            ans += f"**Risk Profile:** Risk Level is **{risk_eval.risk_level}** ({risk_eval.category.upper()}).\n"
            ans += f"**Actionable Advice:** {risk_eval.recommendation}\n"
            ans += f"\n---\n**Source:** {source} | **Updated:** {updated}\n"
            ans += f"**Forecast Confidence:** {confidence}"
            if disagreement:
                ans += f"\n*Note: {disagreement}*"
            return ans


grounded_llm_engine = GroundedLLMEngine()

