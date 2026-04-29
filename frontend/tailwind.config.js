/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'surface-base': '#212121',    
        'surface-sidebar': '#171717', 
        'surface-card': '#2f2f2f',    
        'surface-hover': '#3a3a3a',
        'border-light': 'transparent',
        'border-active': '#424242',
        'text-primary': '#ececec',
        'text-secondary': '#b4b4b4',
        'text-tertiary': '#94a3b8',
        'accent-emerald': '#10a37f', 
        'accent-iris': '#10a37f', // Redirecting iris to emerald to remove blue/purple entirely
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
