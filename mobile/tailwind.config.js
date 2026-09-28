/** @type {import('tailwindcss').Config} */
module.exports = { content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"], presets: [require("nativewind/preset")], theme: { extend: { colors: { clinic: { teal: "#087f78", ink: "#172b3a", canvas: "#f6f9f9" } } } }, plugins: [] };
