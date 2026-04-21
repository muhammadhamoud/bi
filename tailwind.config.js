/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './apps/**/*.py',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#edeff1',
          100: '#d7dce0',
          200: '#b8c0c8',
          300: '#909da8',
          400: '#5f7282',
          500: '#213b52',
          600: '#1e354a',
          700: '#1a2e40',
          800: '#152634',
          900: '#101e29',
          950: '#0c151e',
        },
      },
      boxShadow: {
        soft: '0 10px 30px rgba(2, 6, 23, 0.08)',
        panel: '0 8px 30px rgba(15, 23, 42, 0.18)',
      },
    },
  },
  plugins: [],
}