/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.{html,js}',
    './apps/**/*.{py,html}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef5ff',
          100: '#d9e8ff',
          500: '#1d4ed8',
          600: '#1e40af',
          700: '#1d3a8a',
          900: '#0f172a'
        }
      },
      boxShadow: {
        panel: '0 8px 30px rgba(15, 23, 42, 0.08)'
      }
    },
  },
  plugins: [],
}
