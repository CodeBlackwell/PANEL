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
        chalk: ['Caveat', 'cursive'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'chalk-in': 'chalkIn 0.5s ease-out both',
        'chalk-fade': 'chalkFade 0.6s ease-out both',
        'slide-up': 'slideUp 0.3s ease-out both',
        'score-fill': 'scoreFill 1.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards',
        'line-draw': 'lineDraw 0.8s ease-out both',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'chalk-dust': 'chalkDust 0.3s ease-out both',
      },
      keyframes: {
        chalkIn: {
          '0%': { opacity: '0', filter: 'blur(3px)', transform: 'translateY(6px)' },
          '60%': { opacity: '0.7', filter: 'blur(1px)', transform: 'translateY(1px)' },
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
          '0%': { width: '0%', opacity: '0.5' },
          '20%': { opacity: '1' },
          '100%': { opacity: '1' },
        },
        lineDraw: {
          '0%': { transform: 'scaleX(0)', opacity: '0' },
          '100%': { transform: 'scaleX(1)', opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 4px 1px currentColor', opacity: '1' },
          '50%': { boxShadow: '0 0 12px 4px currentColor', opacity: '0.8' },
        },
        chalkDust: {
          '0%': { opacity: '0.8', transform: 'translateY(0) scale(1)' },
          '100%': { opacity: '0', transform: 'translateY(-8px) scale(0.5)' },
        },
      },
    },
  },
  plugins: [],
}
