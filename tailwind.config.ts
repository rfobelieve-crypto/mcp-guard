import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#050507",
        "bg-2": "#0A0A0C",
        surface: "#0F0F13",
        "surface-2": "#15151B",
        ink: "#F2F3F6",
        "ink-2": "#9AA0AE",
        muted: "#5C6270",
        line: "#1C1D24",
        cyan: "#00E5FF",
        violet: "#9A7BFF",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        sans: [
          "var(--font-sans)",
          "PingFang TC",
          "Microsoft JhengHei",
          "Heiti TC",
          "sans-serif",
        ],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tightest: "-0.045em",
      },
      boxShadow: {
        depth: "0 1px 0 rgba(255,255,255,0.04) inset, 0 24px 60px -24px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(0,229,255,0.25), 0 0 40px rgba(0,229,255,0.12)",
      },
    },
  },
  plugins: [],
};
export default config;
