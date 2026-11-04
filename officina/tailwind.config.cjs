// Tema solo da token: niente colori o misure di default di Tailwind.
const tokens = require("./tailwind.tokens.cjs");
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    ...tokens,
    colors: { ...tokens.colors, transparent: "transparent", current: "currentColor" },
    extend: {},
  },
  plugins: [],
};
