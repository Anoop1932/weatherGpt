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
      console.warn("Speech recognition error event:", event.error);
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
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
};

export const speakText = (text, language = 'en', onStart, onEnd) => {
  if (!('speechSynthesis' in window) || !text) return;

  // Cancel any active speech first
  window.speechSynthesis.cancel();

  // Strip technical metadata footer lines ("---", "Source:", "Updated:", "Confidence:")
  let contentOnly = text.split(/---|\*\*Source:\*\*|\*\*ਸਰੋਤ:\*\*|\*\*स्रोत:\*\*/i)[0];

  // Clean markdown syntax & technical symbols for 100% natural TTS speech
  const isHindiScript = /[\u0900-\u097F]/.test(text) || language === 'hi';
  const isPunjabiScript = /[\u0A00-\u0A7F]/.test(text) || language === 'pa';

  let cleanText = contentOnly
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/#/g, '')
    .replace(/_/g, '')
    .replace(/`/g, '')
    .replace(/--/g, '')
    .replace(/\[.*?\]\(.*?\)/g, '')
    .replace(/\{.*?\}/g, '');

  if (isHindiScript) {
    cleanText = cleanText
      .replace(/%/g, ' प्रतिशत')
      .replace(/°C/g, ' डिग्री सेल्सियस')
      .replace(/km\/h/g, ' किलोमीटर प्रति घंटा')
      .replace(/mm/g, ' मिलीमीटर');
  } else if (isPunjabiScript) {
    cleanText = cleanText
      .replace(/%/g, ' ਪ੍ਰਤੀਸ਼ਤ')
      .replace(/°C/g, ' ਡਿਗਰੀ ਸੈਲਸੀਅਸ')
      .replace(/km\/h/g, ' ਕਿਲੋਮੀਟਰ ਪ੍ਰਤੀ ਘੰਟਾ')
      .replace(/mm/g, ' ਮਿਲੀਮੀਟਰ');
  } else {
    cleanText = cleanText
      .replace(/%/g, ' percent')
      .replace(/°C/g, ' degrees Celsius')
      .replace(/km\/h/g, ' kilometers per hour')
      .replace(/mm/g, ' millimeters');
  }

  cleanText = cleanText.slice(0, 350).trim();

  const utterance = new SpeechSynthesisUtterance(cleanText);

  if (isPunjabiScript) {
    utterance.lang = 'pa-IN';
  } else if (isHindiScript) {
    utterance.lang = 'hi-IN';
  } else {
    utterance.lang = 'en-IN';
  }

  utterance.rate = 0.95;
  utterance.pitch = 1.0;

  // Dynamically inspect browser TTS voices for native or closest matching voice
  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    let targetVoice = null;
    if (isPunjabiScript) {
      targetVoice = voices.find(v => v.lang.includes('pa') || v.name.toLowerCase().includes('punjabi'));
    }
    if (!targetVoice && (isHindiScript || isPunjabiScript)) {
      targetVoice = voices.find(v => v.lang.includes('hi') || v.lang.includes('HI') || v.name.toLowerCase().includes('hindi'));
    }
    if (!targetVoice) {
      targetVoice = voices.find(v => v.lang.includes(utterance.lang) || v.lang.startsWith(utterance.lang.slice(0, 2)));
    }
    if (targetVoice) {
      utterance.voice = targetVoice;
    }
  }

  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  utterance.onerror = (e) => {
    console.warn("TTS Error:", e);
    if (onEnd) onEnd();
  };

  window.speechSynthesis.speak(utterance);
};
