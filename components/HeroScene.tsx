"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const AuditCoreScene = dynamic(() => import("./AuditCoreScene"), {
  ssr: false,
  loading: () => null,
});

/**
 * three.js/@react-three/fiber 是這個頁面最重的一塊 JS(獨立 chunk)。
 * 用 next/dynamic(ssr:false) 拆出去,並且延到瀏覽器閒置或首次繪製後才掛載,
 * 避免它擋到 hero 文字的首次繪製——LCP 元素應該是文案,不是這顆球。
 */
export default function HeroScene(props: {
  verdictRatio: { pass: number; warn: number; crit: number };
}) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const ric =
      (window as any).requestIdleCallback || ((cb: () => void) => setTimeout(cb, 200));
    const id = ric(() => setReady(true));
    return () => {
      const cic = (window as any).cancelIdleCallback;
      if (cic) cic(id);
    };
  }, []);

  if (!ready) return null;
  return <AuditCoreScene {...props} />;
}
