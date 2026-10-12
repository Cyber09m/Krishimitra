/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Deep paddy-field green — the base, not black, not cream.
        field: {
          DEFAULT: "#16302A",
          light: "#1F4038",
          lighter: "#2A5349",
        },
        // Turmeric gold — primary accent, warmth + optimism.
        turmeric: {
          DEFAULT: "#E8A93D",
          dark: "#C68A28",
        },
        // Monsoon sky blue — secondary accent, water/irrigation cues.
        monsoon: {
          DEFAULT: "#3E8FB0",
          dark: "#2C6E8A",
        },
        // Soil brown — tertiary accent, grounding/earth cues.
        soil: {
          DEFAULT: "#8B5E34",
          dark: "#6B4423",
        },
        // Wheat parchment — text/foreground on dark backgrounds.
        wheat: {
          DEFAULT: "#F1EAD7",
          dim: "#C9C2AF",
        },
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        body: ["Work Sans", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
