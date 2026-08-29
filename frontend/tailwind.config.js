/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      spacing: {
        // shared chrome dimensions — keep the sticky header, scroll anchors and
        // the sticky inspector on one source of truth
        header: '3.5rem', // matches the App header height (h-14)
        sticky: '4.5rem', // header + 16px breathing room
      },
      colors: {
        canvas: '#F7F6F2',
        surface: {
          DEFAULT: '#FFFFFF',
          inset: '#F5F3EE',
        },
        hairline: {
          DEFAULT: '#E7E3DB',
          strong: '#D9D4C9',
        },
        ink: {
          DEFAULT: '#191E28',
          soft: '#484F5C',
          faint: '#787E8A',
        },
        primary: {
          DEFAULT: '#2946C6',
          hover: '#2039A9',
          press: '#18276F',
          subtle: '#EEF2FF',
          border: '#CAD3F5',
        },
        positive: {
          DEFAULT: '#2E7A54',
          subtle: '#E9F3EC',
          border: '#BFDECB',
        },
        caution: {
          DEFAULT: '#9A6A1C',
          subtle: '#FAF1DF',
          border: '#E9D5AE',
        },
        critical: {
          DEFAULT: '#BE3B3B',
          subtle: '#FAEBEB',
          border: '#EDC5C5',
        },
      },
      borderRadius: {
        sm: '4px',
        md: '6px',
        lg: '8px',
        xl: '10px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(20,26,40,0.04)',
        raised:
          '0 1px 2px rgba(20,26,40,0.04), 0 8px 20px -8px rgba(20,26,40,0.10), 0 2px 6px -3px rgba(20,26,40,0.06)',
        overlay: '0 24px 60px -12px rgba(16,22,38,0.28), 0 8px 24px -10px rgba(16,22,38,0.16)',
        inset: 'inset 0 1px 2px rgba(20,26,40,0.05)',
      },
      fontSize: {
        meta: ['12px', { lineHeight: '16px' }],
        helper: ['12px', { lineHeight: '16px' }],
        label: ['12.5px', { lineHeight: '16px', letterSpacing: '0.002em' }],
        body: ['14px', { lineHeight: '21px' }],
        input: ['14px', { lineHeight: '20px' }],
        bodylg: ['15px', { lineHeight: '23px' }],
        section: ['16px', { lineHeight: '22px', letterSpacing: '-0.008em' }],
        title: ['20px', { lineHeight: '27px', letterSpacing: '-0.014em' }],
        page: ['29px', { lineHeight: '34px', letterSpacing: '-0.021em' }],
        display: ['30px', { lineHeight: '37px', letterSpacing: '-0.022em' }],
      },
      transitionTimingFunction: {
        swift: 'cubic-bezier(0.2, 0, 0, 1)',
      },
      keyframes: {
        'fade-in': { from: { opacity: '0' }, to: { opacity: '1' } },
        'fade-scale': {
          from: { opacity: '0', transform: 'translateY(6px) scale(0.985)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        'slide-down': {
          from: { opacity: '0', transform: 'translateY(-4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
      },
      animation: {
        'fade-in': 'fade-in 140ms cubic-bezier(0.2,0,0,1)',
        'fade-scale': 'fade-scale 160ms cubic-bezier(0.2,0,0,1)',
        'slide-down': 'slide-down 140ms cubic-bezier(0.2,0,0,1)',
      },
    },
  },
  plugins: [],
}
