/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b1220",
        panel: "#111b2e",
        line: "#25334e",
        rescue: "#36d5a3",
        water: "#38bdf8",
      },
      boxShadow: {
        panel: "0 20px 50px rgba(0, 0, 0, 0.24)",
      },
    },
  },
  plugins: [],
};
