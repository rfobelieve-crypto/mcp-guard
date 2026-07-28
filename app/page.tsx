import CursorLight from "@/components/CursorLight";
import HoloCard from "@/components/HoloCard";
import Reveal from "@/components/Reveal";
import HeroScene from "@/components/HeroScene";
import { getStats } from "@/lib/stats";

const GATES = [
  {
    href: "registry/",
    title: "稽核總表",
    desc: "熱門 MCP 的完整結果，可依風險篩選、搜尋，點開能一路追到證據的檔案路徑與原文片段。",
  },
  {
    href: "method/",
    title: "怎麼查的",
    desc: "六項檢查各自抓什麼，以及 MCP 獨有的那個攻擊面：一段模型讀得到、你讀不到的指令。",
  },
  {
    href: "trust/",
    title: "為什麼可信",
    desc: "一個被瘋傳卻不存在的 MCP、這個工具自己誤報過的 9 次，以及被列出的專案維護者可以怎麼要求更正。",
  },
];

export default function Home() {
  const stats = getStats();

  return (
    <>
      <CursorLight />
      <main className="relative z-10">
        <section className="relative flex min-h-[100svh] items-center overflow-hidden border-b border-line">
          <div className="pointer-events-none absolute inset-y-0 right-[-8%] w-[70%] opacity-90">
            <HeroScene verdictRatio={stats.ratio} />
          </div>
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_70%_55%_at_45%_50%,transparent_0%,rgba(5,5,7,0.4)_58%,#050507_100%)]" />

          <div className="relative mx-auto w-full max-w-[1200px] px-6 py-32">
            <Reveal>
              <p className="font-mono text-[11px] tracking-[0.3em] text-cyan/80">
                獨立稽核 · 繁體中文
              </p>
            </Reveal>
            <Reveal delay={80}>
              <h1 className="mt-6 max-w-[16ch] font-display text-[clamp(40px,7.4vw,88px)] font-black leading-[1.02] tracking-tightest text-ink">
                裝下去之前，
                <br />
                先知道它<span className="text-cyan">要什麼權限</span>。
              </h1>
            </Reveal>
            <Reveal delay={160}>
              <p className="mt-8 max-w-[46ch] text-[clamp(15px,1.6vw,18px)] leading-[1.8] text-ink-2">
                一個 MCP 拿到的不只是你的檔案，而是你正在用的那個 AI
                會被誰下指令。我們逐一稽核，每個結論都附你能自己複現的證據。
              </p>
            </Reveal>
            <Reveal delay={240}>
              <div className="mt-11 flex flex-wrap items-center gap-4">
                <code className="rounded-lg border border-line bg-surface px-5 py-3 font-mono text-sm text-cyan shadow-depth">
                  mcp-guard owner/repo
                </code>
                <a
                  href="registry/"
                  className="border-b border-line pb-1 text-sm text-ink-2 transition hover:border-cyan hover:text-ink"
                >
                  看 {stats.total} 份稽核結果 →
                </a>
              </div>
            </Reveal>
            <Reveal delay={320}>
              <div className="mt-16 flex flex-wrap gap-10 font-mono text-[11px] tracking-wide text-muted">
                <Stat value={stats.pass} label="未發現明顯風險" />
                <Stat value={stats.warn} label="需人工複核" />
                <Stat value={stats.totalFindings} label="累計檢查發現" />
                <div>
                  <b className="block text-[26px] font-bold tracking-tight text-ink">
                    每日
                  </b>
                  自動重新驗證
                </div>
              </div>
            </Reveal>
          </div>
        </section>

        <section className="border-b border-line bg-bg-2 py-28">
          <div className="mx-auto max-w-[1200px] px-6">
            <Reveal>
              <p className="font-mono text-[11px] tracking-[0.3em] text-cyan/80">
                從哪裡開始
              </p>
              <h2 className="mt-4 max-w-[20ch] font-display text-[clamp(28px,3.6vw,44px)] font-black tracking-tight text-ink">
                你想知道哪一件事？
              </h2>
            </Reveal>

            <div className="mt-14 grid gap-6 md:grid-cols-3">
              {GATES.map((g, i) => (
                <Reveal delay={i * 90} key={g.href}>
                  <a href={g.href} className="block h-full">
                    <HoloCard className="h-full p-8">
                      <h3 className="font-display text-xl font-bold text-ink">
                        {g.title}
                      </h3>
                      <p className="mt-4 text-sm leading-[1.8] text-ink-2">
                        {g.desc}
                      </p>
                      <span className="mt-6 inline-block text-cyan transition group-hover:translate-x-1">
                        →
                      </span>
                    </HoloCard>
                  </a>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <footer className="py-14 text-center font-mono text-[11px] tracking-wide text-muted">
          最近一次驗證 {stats.scannedAt} ・{" "}
          <a
            href="https://github.com/rfobelieve-crypto/mcp-guard"
            className="text-cyan hover:underline"
          >
            GitHub ↗
          </a>
        </footer>
      </main>
    </>
  );
}

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div>
      <b className="block text-[26px] font-bold tracking-tight text-ink">
        {value}
      </b>
      {label}
    </div>
  );
}
