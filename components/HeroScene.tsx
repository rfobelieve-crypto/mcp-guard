"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const AuditCoreScene = dynamic(() => import("./AuditCoreScene"), {
  ssr: false,
  loading: () => null,
});

/**
 * three.js/@react-three/fiber 是這個頁面最重的一塊 JS(獨立 chunk,
 * 實測 ~1.2MB)。實測發現只用 requestIdleCallback 不夠——它在
 * hydration 剛完成、主執行緒還沒被其他事佔用時幾乎立刻觸發,
 * 這塊重 JS 照樣在 hero 文字真正定案為 LCP 之前就開始下載/解析/執行,
 * 反而佔用主執行緒讓文字的 paint 被延後。改成明確等 window 'load'
 * 事件(確保關鍵資源已經處理完)之後,再疊加一段固定緩衝,
 * 讓文字有乾淨的時間先畫出來、穩定成 LCP,3D 場景再進場。
 */
export default function HeroScene(props: {
  verdictRatio: { pass: number; warn: number; crit: number };
}) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let idleId: number | undefined;
    let timeoutId: number | undefined;

    const scheduleIdle = () => {
      const ric =
        (window as any).requestIdleCallback ||
        ((cb: () => void) => window.setTimeout(cb, 300));
      idleId = ric(() => setReady(true));
    };

    const onLoad = () => {
      timeoutId = window.setTimeout(scheduleIdle, 600);
    };

    if (document.readyState === "complete") {
      onLoad();
    } else {
      window.addEventListener("load", onLoad, { once: true });
    }

    return () => {
      window.removeEventListener("load", onLoad);
      if (timeoutId) window.clearTimeout(timeoutId);
      const cic = (window as any).cancelIdleCallback;
      if (cic && idleId !== undefined) cic(idleId);
    };
  }, []);

  if (!ready) return null;
  return <AuditCoreScene {...props} />;
}
