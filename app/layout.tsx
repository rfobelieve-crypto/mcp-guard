import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-mono",
  display: "swap",
});

// 內文中文字刻意不用 next/font/google 的 Noto Sans TC:實測發現即使宣告
// subsets:['latin'],Google 仍把完整 CJK unicode-range 一併送出——
// 301KB 的 CSS + 一整批 30-85KB 的字型檔,在節流網路下直接把 FCP 拖到
// 6 秒以上,是先前那版 35-44 分的真正主因,不是 3D 場景。
// 這正是 site.py 自己的註解警告過的陷阱(「整套繁中字型是 5–10MB」)——
// 內文交給系統 CJK 字型即可,見 tailwind.config.ts 的 fontFamily.sans。

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
    <html lang="zh-Hant" className={mono.variable}>
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
