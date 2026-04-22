/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"LXGW WenKai"',
          '"PingFang SC"',
          '"Hiragino Sans GB"',
          '"Microsoft YaHei"',
          'sans-serif',
        ],
        display: [
          '"LXGW WenKai"',
          '"Palatino Linotype"',
          '"Times New Roman"',
          '"STSong"',
          'serif',
        ],
      },
      borderRadius: {
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
      },
      colors: {
        primary: {
          DEFAULT: 'var(--primary-color, #F4A4B4)',
          soft: 'var(--primary-soft, rgba(244, 164, 180, 0.18))',
        },
        accent: {
          DEFAULT: 'var(--accent-color, #C9B1FF)',
        },
        surface: {
          DEFAULT: 'var(--surface-color, #FFFFFF)',
          raised: 'var(--surface-raised)',
          soft: 'var(--surface-soft)',
          panel: 'var(--surface-panel-bg)',
          card: 'var(--surface-card-bg)',
          input: 'var(--surface-input-bg)',
        },
        muted: {
          DEFAULT: 'var(--text-secondary, #7A7A7A)',
        },
      },
    },
  },
  plugins: [],
}
