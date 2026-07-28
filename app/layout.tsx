import type { Metadata } from "next";
import { JetBrains_Mono, Noto_Sans_TC } from "next/font/google";
import "./globals.css";

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-mono",
  display: "swap",
});

// 內文中文字：Noto Sans TC 子集只抓實際用到的字重，體感仍是系統字的補強而非
// 取代——CJK 全字集網頁字型動輒數 MB，不值得為了「不用系統字」犧牲效能。
const sansTC = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "MCP 安檢 · mcp-guard",
  description:
    "安裝任何 MCP 之前，先看清楚它是誰、要什麼權限、有沒有對模型下暗示。",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-Hant" className={`${mono.variable} ${sansTC.variable}`}>
      <body className="grain font-sans antialiased">
        <div
          className="pointer-events-none fixed inset-0 z-30"
          style={{
            background:
              "radial-gradient(1200px 600px at 50% -10%, rgba(0,229,255,0.06), transparent 60%)",
          }}
        />
        {children}
      </body>
    </html>
  );
}
