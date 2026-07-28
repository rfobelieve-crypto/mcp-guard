/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // 靜態匯出：只重做首頁,其餘頁面(/registry /method /pick /trust)
  // 仍由 site.py 產生,部署時把兩邊輸出合併進同一個 site/ 目錄。
  // 見 UX-TASK-BRIEF.md 降風險計畫第 1 條——先做首頁原型,不動其他頁。
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
