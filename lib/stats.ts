import fs from "node:fs";
import path from "node:path";

export type Stats = {
  total: number;
  pass: number;
  warn: number;
  crit: number;
  totalFindings: number;
  scannedAt: string;
  ratio: { pass: number; warn: number; crit: number };
};

/** 首頁統計數字直接讀 reports/data.json,不手打——跟 site.py 用同一份
 *  真實資料來源,避免兩邊網站顯示的數字兜不起來。 */
export function getStats(): Stats {
  const raw = fs.readFileSync(
    path.join(process.cwd(), "reports", "data.json"),
    "utf-8"
  );
  const data = JSON.parse(raw) as {
    scanned_at: string;
    projects: { verdict: string; findings: unknown[] }[];
  };

  let pass = 0;
  let warn = 0;
  let crit = 0;
  let totalFindings = 0;
  for (const p of data.projects) {
    totalFindings += p.findings.length;
    if (p.verdict.startsWith("🟢")) pass++;
    else if (p.verdict.startsWith("🟡")) warn++;
    else if (p.verdict.startsWith("🔴")) crit++;
  }
  const total = data.projects.length;
  return {
    total,
    pass,
    warn,
    crit,
    totalFindings,
    scannedAt: data.scanned_at,
    ratio: {
      pass: pass / total,
      warn: warn / total,
      crit: crit / total,
    },
  };
}
