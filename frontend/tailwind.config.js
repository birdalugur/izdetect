/** @type {import('tailwindcss').Config} */
export default {
  content: ['./public/**/*.html', './src/**/*.{html,js,svelte}'],
  theme: {
    extend: {
      backdropBlur: {
        sm: '4px',
        md: '8px',
        lg: '16px',
      },
    },
  },
  plugins: [
    // require('@tailwindcss/forms'),
  ],
};
