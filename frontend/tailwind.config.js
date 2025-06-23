module.exports = {
   content: [
    "../backend/templates/**/*.html",
  ],
  safelist: ['swiper-slide', 'swiper-wrapper', 'swiper', 'swiper-button-next', 'swiper-button-prev'],
  theme: {
    extend: {
       animation: {
        fadeInUp: 'fadeInUp 0.8s ease-out'
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        }
      },
      colors: {
        dark: "#1B262C",
        navy: "#0F4C75",
        blue: "#3282B8",
        lightBlue: "#BBE1FA",
        maroon: "#9A3B3B",
        offWhite: "#F9F7F7",
        teal: "#00ADB5",
      },
    },
  },
  plugins: [],
}