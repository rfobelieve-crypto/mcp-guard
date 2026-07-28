"use client";

import { useEffect, useRef } from "react";

/** 滑鼠跟隨的柔光——克制、慢速,不是遊標特效。用 rAF 節流,避免每個
 *  mousemove 都觸發 React re-render。 */
export default function CursorLight() {
  const ref = useRef<HTMLDivElement>(null);
  const target = useRef({ x: 0.5, y: 0.35 });
  const current = useRef({ x: 0.5, y: 0.35 });

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;

    const onMove = (e: PointerEvent) => {
      target.current = {
        x: e.clientX / window.innerWidth,
        y: e.clientY / window.innerHeight,
      };
    };

    const tick = () => {
      const c = current.current;
      const t = target.current;
      c.x += (t.x - c.x) * 0.06;
      c.y += (t.y - c.y) * 0.06;
      if (ref.current) {
        ref.current.style.background = `radial-gradient(560px circle at ${
          c.x * 100
        }% ${c.y * 100}%, rgba(0,229,255,0.07), rgba(154,123,255,0.04) 42%, transparent 70%)`;
      }
      raf = requestAnimationFrame(tick);
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    raf = requestAnimationFrame(tick);
    return () => {
      window.removeEventListener("pointermove", onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none fixed inset-0 z-20 transition-opacity"
    />
  );
}
