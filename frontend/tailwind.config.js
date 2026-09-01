/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'sans-serif'],
        arabic: ['Noto Naskh Arabic', 'sans-serif'],
      },
      colors: {
        theme: {
          bg: '#070A12',
          surface: '#0F172A',
          elevated: '#1E293B',
          border: '#334155',
          primary: '#0EA5E9',
          accent: '#8B5CF6',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E',
        }
      }
    },
  },
  plugins: [],
}
