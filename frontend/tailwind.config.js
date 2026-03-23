/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Euler's Blackboard palette
        slate: {
          DEFAULT: '#1e2127',
          light: '#282c34',
          border: '#353a44',
        },
        chalk: {
          DEFAULT: '#e8e4dc',
          dim: '#a8a49c',
          faint: '#6b6760',
        },
        dusty: {
          DEFAULT: '#6b8cae',
          light: '#8aa8c8',
          dim: '#4a6a8a',
        },
        yellow: {
          DEFAULT: '#e8d88c',
          dim: '#c4b66e',
        },
        // Muted chalk agent colors
        agent: {
          arch: '#7eaac4',
          devops: '#7cb88c',
          security: '#c47e7e',
          ux: '#a77ec4',
          qa: '#c4b87e',
          pm: '#c47eaa',
          data: '#7ec4c4',
          ml: '#c4a07e',
          frontend: '#7e8cc4',
          backend: '#7ec4a0',
          mobile: '#c47e94',
          ba: '#c4b07e',
          lead: '#7ec4b0',
          mod: '#8a8a8a',
          clarifier: '#9a7ec4',
          judge: '#7e94c4',
        },
      },
      fontFamily: {
        heading: ['"STIX Two Text"', 'Spectral', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'chalk-in': 'chalkIn 0.4s ease-out',
        'chalk-fade': 'chalkFade 0.6s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'score-fill': 'scoreFill 1.2s ease-out forwards',
      },
      keyframes: {
        chalkIn: {
          '0%': { opacity: '0', filter: 'blur(2px)', transform: 'translateY(4px)' },
          '100%': { opacity: '1', filter: 'blur(0)', transform: 'translateY(0)' },
        },
        chalkFade: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scoreFill: {
          '0%': { width: '0%' },
        },
      },
    },
  },
  plugins: [],
}
