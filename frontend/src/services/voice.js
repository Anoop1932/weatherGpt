// Speech Recognition & Speech Synthesis (TTS) Service for WeatherGPT

let cachedVoices = [];

export const initVoices = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;

  const updateVoices = () => {
    const list = window.speechSynthesis.getVoices();
    if (list && list.length > 0) {
      cachedVoices = list;
    }
  };

  updateVoices();
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = updateVoices;
  }
};

// Initialize voices immediately on load
initVoices();

export const getAvailableVoices = () => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return [];
  const current = window.speechSynthesis.getVoices();
  if (current && current.length > 0) {
    cachedVoices = current;
    return current;
  }
  return cachedVoices;
};

/**
 * Reusable language-aware voice selection function.
 * Matches browser voices according to exact locale -> base language prefix -> name keywords -> fallback.
 * Guarantees that Hindi/Punjabi will not use a foreign/English voice when an Indic voice is available.
 */
export const getBestVoice = (language = 'en', voicesList = null) => {
  const voices = (voicesList && voicesList.length > 0) ? voicesList : getAvailableVoices();
  if (!voices || voices.length === 0) return null;

  const langCode = (language || 'en').toLowerCase().replace('_', '-');
  const baseLang = langCode.split('-')[0]; // 'hi', 'pa', 'en'

  const norm = (str) => (str || '').toLowerCase().replace('_', '-');

  // Priority preferred locales by base language
  const preferredLocales = {
    hi: ['hi-in', 'hi'],
    pa: ['pa-in', 'pa'],
    en: ['en-in', 'en-us', 'en-gb', 'en']
  };

  const targetLocales = preferredLocales[baseLang] || [langCode, baseLang];

  // 1. Exact locale match (e.g. hi-IN for Hindi, pa-IN for Punjabi, en-IN for English)
  for (const loc of targetLocales) {
    const exactVoice = voices.find(v => norm(v.lang) === loc);
    if (exactVoice) return exactVoice;
  }

  // 2. Base language prefix match (e.g. startsWith('hi-') or startsWith('hi'))
  const baseVoice = voices.find(v => norm(v.lang).startsWith(baseLang + '-'));
  if (baseVoice) return baseVoice;

  const basePrefixVoice = voices.find(v => norm(v.lang).startsWith(baseLang));
  if (basePrefixVoice) return basePrefixVoice;

  // 3. Name check keywords for native voice naming
  if (baseLang === 'hi') {
    const nameMatch = voices.find(v => /hindi|हिन्दी/i.test(v.name));
    if (nameMatch) return nameMatch;
    // If no Hindi voice is installed on machine, prefer an Indian English voice (en-IN)
    // which has natural Indic phonology, instead of a foreign US/UK voice
    const indianVoice = voices.find(v => norm(v.lang) === 'en-in' || /india/i.test(v.name));
    if (indianVoice) return indianVoice;
  } else if (baseLang === 'pa') {
    const nameMatch = voices.find(v => /punjabi|ਪੰਜਾਬੀ/i.test(v.name));
    if (nameMatch) return nameMatch;
    // Fallback for Punjabi: Indian Hindi voice (hi-IN) handles Indic phonetics accurately
    const hindiVoice = voices.find(v => norm(v.lang).startsWith('hi') || /hindi|हिन्दी/i.test(v.name));
    if (hindiVoice) return hindiVoice;
    const indianVoice = voices.find(v => norm(v.lang) === 'en-in' || /india/i.test(v.name));
    if (indianVoice) return indianVoice;
  } else if (baseLang === 'en') {
    const enVoice = voices.find(v => norm(v.lang).startsWith('en'));
    if (enVoice) return enVoice;
  }

  // 4. Default fallback voice
  const defaultVoice = voices.find(v => v.default);
  return defaultVoice || voices[0] || null;
};

/**
 * Detects the actual spoken language of the response text.
 * Gives precedence to Devanagari/Gurmukhi scripts and Hinglish lexical markers.
 */
export const detectResponseLanguage = (text, languageHint = 'en') => {
  if (!text) return languageHint;

  // 1. Devanagari script (Hindi, Marathi, etc.)
  if (/[\u0900-\u097F]/.test(text)) {
    return 'hi';
  }

  // 2. Gurmukhi script (Punjabi)
  if (/[\u0A00-\u0A7F]/.test(text)) {
    return 'pa';
  }

  // 3. Roman Hinglish tokens
  const hinglishTokens = [
    /\b(aaj|kal|parso|barish|baarish|mausam|taapman|tapman|kaisa|kaisa\s+hai|kaise|kya|hai|hain|hoon|hun|mein|vich|batao|hogi|hoga|rahega|rahegi|badhiya|theek|bhai|dekho|chahiye|kitna|kitni|sambhavna|garmi|thand|dhoop|hawa|pratishat)\b/i
  ];
  if (hinglishTokens.some(regex => regex.test(text))) {
    return 'hi';
  }

  // 4. Roman Punjabi tokens
  const punjabiTokens = [
    /\b(ajj|kallh|parson|meeh|pavega|hovega|dasso|tuhanu|saade|pind|vich|changa|theek\s+aa|kida|kivein)\b/i
  ];
  if (punjabiTokens.some(regex => regex.test(text))) {
    return 'pa';
  }

  // 5. Explicit user language hint if Indic
  if (languageHint === 'hi' || languageHint === 'pa') {
    return languageHint;
  }

  return 'en';
};

/**
 * Strips all emojis, emoticons, pictographs, and dingbats completely.
 * Emojis are never replaced with words (e.g. 🙂 never becomes "smiling face" or "smilkly").
 */
export const stripEmojis = (text) => {
  if (!text) return '';
  let cleaned = text;

  // 1. Unicode Extended_Pictographic regex (covers modern standard & compound emojis)
  try {
    cleaned = cleaned.replace(/\p{Extended_Pictographic}/gu, '');
  } catch (e) {
    cleaned = cleaned.replace(/[\u{1F300}-\u{1F9FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1FA70}-\u{1FAFF}]/gu, '');
  }

  // 2. Explicit symbols, variation selectors, keycap combos, dingbats
  cleaned = cleaned.replace(/[\uFE0E\uFE0F\u200D\u20E3\u25AA-\u25FE\u2600-\u26FF\u2700-\u27BF]/g, '');

  // 3. Emoticons (e.g. :-), :), :-(, :(, :D, :-D, ;), :-P, :p, <3, etc.)
  cleaned = cleaned.replace(/(?:^|\s)(?::[-~]?[)D(PpdOosS3/\\|]|;[-~]?[)D(PpdOosS3/\\|]|<3|x[DdpP])(?:\s|$)/gi, ' ');

  return cleaned;
};

/**
 * Cleans assistant response text specifically for TTS speech output.
 * - Strips emojis, emoticons, decorative bullets, markdown symbols, and technical footer lines.
 * - Expands weather units (32°C -> 32 degrees Celsius / 32 डिग्री सेल्सियस, 70% -> 70 percent / 70 प्रतिशत).
 * - Preserves native Devanagari script for Hindi TTS (no transliteration).
 */
export const cleanTextForSpeech = (text, lang) => {
  if (!text) return '';

  // 1. Strip technical metadata footer lines ("---", "Source:", "Confidence:")
  let content = text.split(/---|\*\*Source:\*\*|\*\*ਸਰੋਤ:\*\*|\*\*स्रोत:\*\*|WeatherGPT Intelligence Engine/i)[0];

  // 2. Strip markdown links [label](url) -> label
  content = content.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // 3. Strip raw URLs
  content = content.replace(/https?:\/\/\S+/gi, '');

  // 4. Strip SVG and HTML tags
  content = content.replace(/<svg[\s\S]*?<\/svg>/gi, '');
  content = content.replace(/<[^>]+>/g, '');
  content = content.replace(/\b(?:svg|SVG)\b/g, '');
  content = content.replace(/svg[A-Za-z0-9_\-\s:]+svg/gi, '');

  // Strip UI badge tokens (e.g. LOW RISK, MODERATE RISK, HIGH RISK)
  content = content.replace(/\b(?:LOW|MODERATE|HIGH|SEVERE)\s+RISK\b/gi, '');

  // Expand UI prefixes (Max:, Min:, Cond:) to clean spoken words
  content = content
    .replace(/\bMax:\s*/gi, 'Maximum ')
    .replace(/\bMin:\s*/gi, 'Minimum ')
    .replace(/\bCond:\s*/gi, 'Condition: ');

  // 5. Strip emojis and emoticons completely
  content = stripEmojis(content);

  // 6. Strip decorative bullets and list markers at line starts
  content = content.replace(/^[•●▪▫◆★☆\-\*\+]\s+/gm, '');

  // 7. Strip markdown formatting symbols (bold, italic, code, headings)
  content = content
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/#{1,6}\s+/g, '')
    .replace(/`{1,3}[^`]*`{1,3}/g, '')
    .replace(/`/g, '')
    .replace(/_{1,2}/g, '');

  // 8. Natural weather units expansion according to language
  if (lang === 'hi') {
    content = content
      .replace(/(\d+(?:\.\d+)?)\s*%/g, '$1 प्रतिशत')
      .replace(/(\d+(?:\.\d+)?)\s*°\s*C\b/gi, '$1 डिग्री सेल्सियस')
      .replace(/°\s*C\b/gi, ' डिग्री सेल्सियस')
      .replace(/(\d+(?:\.\d+)?)\s*km\/h\b/gi, '$1 किलोमीटर प्रति घंटा')
      .replace(/(\d+(?:\.\d+)?)\s*kmph\b/gi, '$1 किलोमीटर प्रति घंटा')
      .replace(/(\d+(?:\.\d+)?)\s*mm\b/gi, '$1 मिलीमीटर');
  } else if (lang === 'pa') {
    content = content
      .replace(/(\d+(?:\.\d+)?)\s*%/g, '$1 ਪ੍ਰਤੀਸ਼ਤ')
      .replace(/(\d+(?:\.\d+)?)\s*°\s*C\b/gi, '$1 ਡਿਗਰੀ ਸੈਲਸੀਅਸ')
      .replace(/°\s*C\b/gi, ' ਡਿਗਰੀ ਸੈਲਸੀਅਸ')
      .replace(/(\d+(?:\.\d+)?)\s*km\/h\b/gi, '$1 ਕਿਲੋਮੀਟਰ ਪ੍ਰਤੀ ਘੰਟਾ')
      .replace(/(\d+(?:\.\d+)?)\s*kmph\b/gi, '$1 ਕਿਲੋਮੀਟਰ ਪ੍ਰਤੀ ਘੰਟਾ')
      .replace(/(\d+(?:\.\d+)?)\s*mm\b/gi, '$1 ਮਿਲੀਮੀਟਰ');
  } else {
    content = content
      .replace(/(\d+(?:\.\d+)?)\s*%/g, '$1 percent')
      .replace(/(\d+(?:\.\d+)?)\s*°\s*C\b/gi, '$1 degrees Celsius')
      .replace(/°\s*C\b/gi, ' degrees Celsius')
      .replace(/(\d+(?:\.\d+)?)\s*km\/h\b/gi, '$1 kilometers per hour')
      .replace(/(\d+(?:\.\d+)?)\s*kmph\b/gi, '$1 kilometers per hour')
      .replace(/(\d+(?:\.\d+)?)\s*mm\b/gi, '$1 millimeters');
  }

  // 9. Normalize excessive whitespace, colons, and punctuation
  content = content
    .replace(/\s*:\s*/g, ': ')
    .replace(/\s+/g, ' ')
    .trim();

  // 10. Ensure sentence pause terminator if missing
  if (content && !/[.!?।|]$/.test(content)) {
    content += (lang === 'hi' || lang === 'pa' ? '।' : '.');
  }

  return content.slice(0, 450).trim();
};

export const isSpeechRecognitionSupported = () => {
  return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
};

export const startVoiceRecognition = (language = 'en', onResult, onError, onEnd) => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    onError && onError('Browser Speech Recognition is not supported on this device.');
    return null;
  }

  try {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    if (language === 'hi') {
      recognition.lang = 'hi-IN';
    } else if (language === 'pa') {
      recognition.lang = 'pa-IN';
    } else {
      recognition.lang = 'en-IN';
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onResult && onResult(transcript);
    };

    recognition.onerror = (event) => {
      console.warn("[SpeechRecognition Warning]:", event.error);
      onError && onError(event.error);
    };

    recognition.onend = () => {
      onEnd && onEnd();
    };

    recognition.start();
    return recognition;
  } catch (err) {
    onError && onError(err.message || "Failed to start voice recognition");
    return null;
  }
};

export const stopSpeaking = () => {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
};

/**
 * Speaks the assistant response text using proper language-aware voice selection.
 * Emojis and markdown are cleanly stripped from the spoken text while leaving the UI intact.
 */
export const speakText = (text, languageHint = 'en', onStart, onEnd) => {
  if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text) return;

  // Always cancel any active speech first to avoid overlapping speech
  window.speechSynthesis.cancel();

  // 1. Detect actual response language
  const detectedLang = detectResponseLanguage(text, languageHint);

  // 2. Clean speech text (strip emojis, markdown, expand units)
  const cleanText = cleanTextForSpeech(text, detectedLang);
  if (!cleanText) return;

  const utterance = new SpeechSynthesisUtterance(cleanText);

  const localeMap = {
    hi: 'hi-IN',
    pa: 'pa-IN',
    en: 'en-IN'
  };
  const targetLocale = localeMap[detectedLang] || 'en-IN';

  let hasAttemptedFallback = false;

  const doSpeak = () => {
    window.speechSynthesis.cancel();

    const selectedVoice = getBestVoice(detectedLang);
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      utterance.lang = selectedVoice.lang;
    } else {
      utterance.lang = targetLocale;
    }

    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    if (onStart) utterance.onstart = onStart;
    if (onEnd) utterance.onend = onEnd;

    utterance.onerror = (e) => {
      // Normal speech interruption or cancellation is expected when users switch queries or stop speech
      if (e.error === 'canceled' || e.error === 'interrupted') {
        console.debug("[WeatherGPT TTS] Speech canceled or interrupted normally.");
        if (onEnd) onEnd();
        return;
      }

      console.warn("[WeatherGPT TTS Error]:", {
        name: e.name || 'SpeechSynthesisErrorEvent',
        error: e.error,
        message: e.message || 'Speech engine error',
        text: utterance.text,
        lang: utterance.lang,
        selectedVoiceName: utterance.voice ? utterance.voice.name : 'None',
        selectedVoiceLang: utterance.voice ? utterance.voice.lang : 'None'
      });

      // Attempt exactly one safe fallback voice without recursive looping
      if (!hasAttemptedFallback) {
        hasAttemptedFallback = true;
        const fallbackVoice = getAvailableVoices().find(v => v.lang.startsWith('en')) || null;
        if (fallbackVoice && fallbackVoice !== utterance.voice) {
          try {
            const fallbackUtterance = new SpeechSynthesisUtterance(cleanText);
            fallbackUtterance.voice = fallbackVoice;
            fallbackUtterance.lang = fallbackVoice.lang;
            fallbackUtterance.onerror = () => { if (onEnd) onEnd(); };
            if (onEnd) fallbackUtterance.onend = onEnd;
            window.speechSynthesis.speak(fallbackUtterance);
            return;
          } catch (retryErr) {
            console.debug("[WeatherGPT TTS] Fallback speech error:", retryErr);
          }
        }
      }

      if (onEnd) onEnd();
    };

    // Print required debug information to browser console without exposing in production UI
    console.log("[WeatherGPT TTS]", {
      detected_language: detectedLang,
      selected_voice_name: selectedVoice ? selectedVoice.name : "Browser Default",
      selected_voice_lang: selectedVoice ? selectedVoice.lang : targetLocale,
      cleaned_speech_text: cleanText
    });

    try {
      window.speechSynthesis.speak(utterance);
    } catch (speakErr) {
      console.warn("[WeatherGPT TTS] speak() call failed:", speakErr);
      if (onEnd) onEnd();
    }
  };

  // Check if voices are loaded or need to wait for voiceschanged
  const voices = getAvailableVoices();
  if (voices.length === 0 && 'onvoiceschanged' in window.speechSynthesis) {
    const onVoicesChangedHandler = () => {
      initVoices();
      window.speechSynthesis.removeEventListener?.('voiceschanged', onVoicesChangedHandler);
      doSpeak();
    };
    window.speechSynthesis.addEventListener?.('voiceschanged', onVoicesChangedHandler, { once: true });
    // Safety timeout in case onvoiceschanged does not fire
    setTimeout(() => {
      if (!utterance.voice) {
        doSpeak();
      }
    }, 200);
  } else {
    doSpeak();
  }
};
