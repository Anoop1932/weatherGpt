import { LOCALES, dictionaries } from './locales';

export { LOCALES };

export const getLocaleInfo = (lang = 'en') => {
  return LOCALES[lang] || LOCALES.en;
};

export const applyTextDirection = (lang = 'en') => {
  const info = getLocaleInfo(lang);
  document.documentElement.dir = info.dir || 'ltr';
  document.documentElement.lang = lang;
};

export const t = (key, lang = 'en') => {
  const dict = dictionaries[lang] || dictionaries.en;
  return dict[key] || dictionaries.en[key] || key;
};
