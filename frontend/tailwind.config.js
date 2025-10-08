/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Glossy Black-Gold Theme
        primary: {
          dark: '#0a0e1a',
          darker: '#060911',
          navy: '#0f1624',
        },
        gold: {
          50: '#fef9e7',
          100: '#fdf3cf',
          200: '#fbe79f',
          300: '#f9db6f',
          400: '#f7cf3f',
          500: '#d4af37',
          600: '#b8942f',
          700: '#9c7827',
          800: '#805d1f',
          900: '#644217',
        },
        accent: {
          blue: '#1a2942',
          lightBlue: '#2a3f5f',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-gold': 'linear-gradient(135deg, #d4af37 0%, #f7cf3f 50%, #d4af37 100%)',
        'gradient-dark': 'linear-gradient(135deg, #0a0e1a 0%, #1a2942 100%)',
        'glossy-gold': 'linear-gradient(145deg, #f7cf3f 0%, #d4af37 35%, #b8942f 70%, #d4af37 100%)',
      },
      boxShadow: {
        'gold-glow': '0 0 20px rgba(212, 175, 55, 0.3), 0 0 40px rgba(212, 175, 55, 0.1)',
        'gold-glow-lg': '0 0 30px rgba(212, 175, 55, 0.4), 0 0 60px rgba(212, 175, 55, 0.2)',
        'inner-glow': 'inset 0 0 20px rgba(212, 175, 55, 0.1)',
        'glossy': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      animation: {
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'slide-in': 'slide-in 0.3s ease-out',
        'slide-in-bottom': 'slide-in-bottom 0.4s ease-out',
        'slide-in-left': 'slide-in-left 0.3s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        'fade-in': 'fade-in 0.5s ease-out',
        'fade-in-up': 'fade-in-up 0.6s ease-out',
        'fade-in-down': 'fade-in-down 0.6s ease-out',
        'scale-in': 'scale-in 0.3s ease-out',
        'bounce-in': 'bounce-in 0.5s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
        'ripple': 'ripple 0.6s ease-out',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { 
            boxShadow: '0 0 20px rgba(212, 175, 55, 0.3)',
          },
          '50%': { 
            boxShadow: '0 0 40px rgba(212, 175, 55, 0.6)',
          },
        },
        'slide-in': {
          '0%': { 
            transform: 'translateY(-10px)', 
            opacity: '0',
          },
          '100%': { 
            transform: 'translateY(0)', 
            opacity: '1',
          },
        },
        'slide-in-bottom': {
          '0%': { 
            transform: 'translateY(20px)', 
            opacity: '0',
          },
          '100%': { 
            transform: 'translateY(0)', 
            opacity: '1',
          },
        },
        'slide-in-left': {
          '0%': { 
            transform: 'translateX(-20px)', 
            opacity: '0',
          },
          '100%': { 
            transform: 'translateX(0)', 
            opacity: '1',
          },
        },
        'slide-in-right': {
          '0%': { 
            transform: 'translateX(20px)', 
            opacity: '0',
          },
          '100%': { 
            transform: 'translateX(0)', 
            opacity: '1',
          },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { 
            opacity: '0',
            transform: 'translateY(10px)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        'fade-in-down': {
          '0%': { 
            opacity: '0',
            transform: 'translateY(-10px)',
          },
          '100%': { 
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        'scale-in': {
          '0%': { 
            transform: 'scale(0.9)',
            opacity: '0',
          },
          '100%': { 
            transform: 'scale(1)',
            opacity: '1',
          },
        },
        'bounce-in': {
          '0%': { 
            transform: 'scale(0.3)',
            opacity: '0',
          },
          '50%': { 
            transform: 'scale(1.05)',
          },
          '70%': { 
            transform: 'scale(0.9)',
          },
          '100%': { 
            transform: 'scale(1)',
            opacity: '1',
          },
        },
        'shimmer': {
          '0%': { 
            backgroundPosition: '-1000px 0',
          },
          '100%': { 
            backgroundPosition: '1000px 0',
          },
        },
        'ripple': {
          '0%': { 
            transform: 'scale(0)',
            opacity: '1',
          },
          '100%': { 
            transform: 'scale(4)',
            opacity: '0',
          },
        },
        'wiggle': {
          '0%, 100%': { 
            transform: 'rotate(-3deg)',
          },
          '50%': { 
            transform: 'rotate(3deg)',
          },
        },
      },
    },
  },
  plugins: [],
}