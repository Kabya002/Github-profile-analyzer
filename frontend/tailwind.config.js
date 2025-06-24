module.exports = {
  content: ["../backend/templates/**/*.html"],
  safelist: [
    "swiper-slide",
    "swiper-wrapper",
    "swiper",
    "swiper-button-next",
    "swiper-button-prev",
  ],
  theme: {
    extend: {
       backgroundImage: {
      'nav-radial': "radial-gradient(circle 1002px at 2.7% 6.8%, rgba(10,38,71,1) 1.2%, rgba(20,66,114,1) 10.3%, rgba(32,82,149,1) 15.8%, rgba(44,116,179,1) 20.3%, rgba(20,66,114,1) 27.6%, rgba(20,66,114,1) 35.2%, rgba(32,82,149,1) 42.7%, rgba(10,38,71,1) 49.5%, rgba(20,66,114,1) 60.4%, rgba(32,82,149,1) 67.8%, rgba(10,38,71,1) 78.7%, rgba(20,66,114,1) 88.2%, rgba(32,82,149,1) 100.1%)",
    },
      animation: {
        fadeInUp: "fadeInUp 0.8s ease-out",
        gradientMove: "gradientMove linear ease infinite",
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        gradientMove: {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
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
};
