import React, { useState, useEffect, useRef } from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import { RiskBadge } from './RiskBadge';
import { startVoiceRecognition, speakText, stopSpeaking } from '../services/voice';
import { getWeatherIcon } from '../utils/weatherIcons';
import { gsap } from 'gsap';
import { 
  Search, 
  Mic, 
  MicOff, 
  Volume2, 
  Square,
  Sparkles, 
  ArrowRight,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  User,
  Bot
} from 'lucide-react';

const FormattedText = ({ text }) => {
  if (!text) return null;
  const blocks = text.split('\n\n');
  return (
    <div className="space-y-2 text-slate-800 dark:text-slate-200">
      {blocks.map((block, bIdx) => {
        if (block.trim() === '---') {
          return <hr key={bIdx} className="border-slate-200 dark:border-slate-700 my-2" />;
        }
        const parts = block.split(/(\*\*.*?\*\*)/g);
        return (
          <p key={bIdx} className="leading-relaxed">
            {parts.map((part, pIdx) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return (
                  <strong key={pIdx} className="font-semibold text-slate-900 dark:text-white">
                    {part.slice(2, -2)}
                  </strong>
                );
              }
              return part;
            })}
          </p>
        );
      })}
    </div>
  );
};

export const ChatWidget = () => {
  const { chatMessages, sendQuery, language, dynamicQuestions } = useWeather();
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatMessages.length > 1) {
      setExpanded(true);
    }
  }, [chatMessages.length]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;

      if (!window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const lastBubble = chatContainerRef.current.querySelector('.chat-message-bubble:last-child');
        if (lastBubble) {
          gsap.fromTo(lastBubble, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' });
        }
      }
    }
  }, [chatMessages.length, isSending, expanded]);

  const handleSend = async (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim() || isSending) return;

    setInputText('');
    setIsSending(true);
    stopSpeaking();
    setIsSpeaking(false);
    setExpanded(true);

    const reply = await sendQuery(query);
    setIsSending(false);

    if (reply && reply.text) {
      speakText(
        reply.text,
        language,
        () => setIsSpeaking(true),
        () => setIsSpeaking(false)
      );
    }
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      setIsListening(false);
      return;
    }

    stopSpeaking();
    setIsSpeaking(false);
    setIsListening(true);

    startVoiceRecognition(
      language,
      (transcript) => {
        setInputText(transcript);
        setIsListening(false);
        handleSend(transcript);
      },
      (err) => {
        console.warn("Voice input error:", err);
        setIsListening(false);
      },
      () => {
        setIsListening(false);
      }
    );
  };

  const handleStopSpeech = () => {
    stopSpeaking();
    setIsSpeaking(false);
  };

  return (
    <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-4 sm:p-5 space-y-3 text-slate-900 dark:text-slate-100 transition-colors">
      {/* Header Info */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700/80 pb-2">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-white">
          <Sparkles className="w-4 h-4 text-sky-600 dark:text-sky-400" />
          <span>{t('app_name', language)} — {t('ai_assistant', language)}</span>
        </div>
        <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">{t('app_tagline', language)}</span>
      </div>

      {/* Input Form Bar with Voice Icon */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isListening ? t('listening', language) : `${t('ask_weathergpt', language)} ("Kal Patna Bihar mein barish hogi?", "Jalandhar weather?")`}
            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm rounded-2xl pl-10 pr-12 py-3 focus:outline-none focus:bg-white dark:focus:bg-slate-700 focus:border-sky-500 transition"
          />

          {/* Voice Mic Toggle Icon */}
          <button
            type="button"
            onClick={handleVoiceToggle}
            className={`absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded-xl transition ${
              isListening
                ? 'bg-rose-50 dark:bg-rose-950 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800 animate-pulse'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700'
            }`}
            title={isListening ? t('listening', language) : t('voice_input', language)}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
        </div>

        {/* Submit Search Button */}
        <button
          type="submit"
          disabled={isSending || !inputText.trim()}
          className="px-4 py-3 bg-sky-600 hover:bg-sky-700 dark:bg-sky-500 dark:hover:bg-sky-600 disabled:opacity-40 text-white font-medium text-xs rounded-2xl flex items-center gap-1.5 transition shrink-0 shadow-xs"
        >
          {isSending ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <ArrowRight className="w-4 h-4" />}
          <span className="hidden sm:inline">{t('ask_ai', language)}</span>
        </button>

        {/* Speech Stop Button */}
        {isSpeaking && (
          <button
            type="button"
            onClick={handleStopSpeech}
            className="p-3 bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-2xl text-xs flex items-center gap-1.5 transition shrink-0"
            title={t('stop_voice', language)}
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            <span className="hidden sm:inline">{t('stop_voice', language)}</span>
          </button>
        )}
      </form>

      {/* Contextual Quick Suggestions & Conversation Items Counter */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
          <span className="text-slate-500 dark:text-slate-400 text-[11px] shrink-0 font-medium">{t('quick_query', language)}:</span>
          {dynamicQuestions.slice(0, 3).map((sq, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleSend(sq)}
              className="text-[11px] bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 shrink-0 transition"
            >
              {sq}
            </button>
          ))}
        </div>

        {chatMessages.length > 0 && (
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="text-[11px] text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 shrink-0 ml-auto font-medium"
          >
            <MessageSquare className="w-3 h-3 text-sky-600 dark:text-sky-400" />
            <span>{chatMessages.length - 1} {t('conversation_items', language)}</span>
            {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        )}
      </div>

      {/* Full Conversation History Drawer */}
      {expanded && (
        <div className="pt-2 border-t border-slate-100 dark:border-slate-700/80 space-y-3">
          <div ref={chatContainerRef} className="max-h-[360px] overflow-y-auto space-y-3 pr-1">
            {chatMessages.map((msg, idx) => {
              const isUser = msg.sender === 'user';
              return (
                <div
                  key={idx}
                  className={`chat-message-bubble flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs shrink-0 ${
                    isUser 
                      ? 'bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800' 
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                  }`}>
                    {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />}
                  </div>

                  <div className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed ${
                    isUser 
                      ? 'bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-slate-900 dark:text-white font-medium rounded-tr-none' 
                      : 'bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-tl-none space-y-2'
                  }`}>
                    {!isUser && (
                      <div className="flex items-center justify-between gap-2 mb-1 pb-1 border-b border-slate-200/80 dark:border-slate-700">
                        <span className="font-bold text-slate-900 dark:text-white text-[11px]">WeatherGPT</span>
                        <div className="flex items-center gap-2">
                          {!msg.is_non_weather && !msg.is_missing_location && (
                            <RiskBadge level={msg.risk_level || 'LOW'} />
                          )}
                          <button
                            type="button"
                            onClick={() => speakText(msg.text, language, () => setIsSpeaking(true), () => setIsSpeaking(false))}
                            className="p-1 rounded text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
                            title="Read aloud"
                          >
                            <Volume2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    )}

                    {isUser ? (
                      <div>{msg.text}</div>
                    ) : (
                      <FormattedText text={msg.text} />
                    )}

                    {!isUser && msg.weather_facts && !msg.is_non_weather && (
                      <div className="mt-2 pt-2 border-t border-slate-200/80 dark:border-slate-700 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                        <div className="flex items-center gap-1">
                          {getWeatherIcon(msg.weather_facts.weather_code, true, "w-3.5 h-3.5")}
                          <span>Max: <strong className="text-slate-800 dark:text-slate-200">{msg.weather_facts.temp_max_c}°C</strong></span>
                        </div>
                        <div>Rain: <strong className="text-slate-800 dark:text-slate-200">{msg.weather_facts.rain_probability}%</strong></div>
                        <div>Wind: <strong className="text-slate-800 dark:text-slate-200">{msg.weather_facts.max_wind_kmh} km/h</strong></div>
                        <div>Cond: <strong className="text-slate-800 dark:text-slate-200">{msg.weather_facts.condition_text}</strong></div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {/* Assistant Typing Loading State */}
            {isSending && (
              <div className="flex items-start gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-800 text-sky-600 dark:text-sky-400 border border-slate-200 dark:border-slate-700 flex items-center justify-center text-xs shrink-0">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-4 py-3 rounded-2xl rounded-tl-none text-xs text-slate-600 dark:text-slate-300 flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-600 dark:text-sky-400" />
                  <span>{t('thinking', language)}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget;
