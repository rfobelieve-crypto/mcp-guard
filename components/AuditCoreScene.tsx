"use client";

import { Component, useMemo, useRef, useState, useEffect } from "react";
import type { ReactNode } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** WebGL 在受限環境(舊裝置、無 GPU 的 headless/虛擬機、部分企業瀏覽器
 *  沙箱)可能直接建立失敗,three.js 會同步丟出例外。R3F 的 Canvas 沒有
 *  內建的失敗回退,而這個例外若沒被接住,會把整個首頁換成 Next.js 的
 *  預設錯誤畫面——等於裝飾動畫的失敗直接讓整頁不可讀,違反「任何 JS
 *  互動失效時,內容仍應可讀」的要求。這裡用 class component 接住它,
 *  退回跟 prefers-reduced-motion 相同的靜態漸層。 */
class SceneErrorBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { errored: boolean }
> {
  state = { errored: false };
  static getDerivedStateFromError() {
    return { errored: true };
  }
  componentDidCatch(err: unknown) {
    console.warn("AuditCoreScene 3D 場景初始化失敗，改用靜態版本：", err);
  }
  render() {
    return this.state.errored ? this.props.fallback : this.props.children;
  }
}

/**
 * 首屏 3D 場景:延續原站「MCP 封包從深空湧向稽核核心,依真實比例分流」的
 * 產品隱喻(見 site.py 的 SCENE_JS docstring),只是這次用真正的 3D 場景做,
 * 而不是手寫透視投影。粒子分流比例吃真實稽核資料(見 verdictRatio props),
 * 不是裝飾性的隨機數字——這點刻意延續,因為這是「稽核工具」而不是「品牌動畫」。
 *
 * 沒有用外部 3D 資產(photorealistic 機器人網格):先用抽象幾何核心 + 粒子流
 * 驗證電影感調性與效能,是否要換成真正雕模/掃描等級的機器人資產,
 * 留給看過這版之後的決定(見 REDESIGN-PROPOSAL.md)。
 */

const COLORS = {
  pass: new THREE.Color("#00E5FF"),
  warn: new THREE.Color("#9A7BFF"),
  crit: new THREE.Color("#F0827A"),
};

function Core() {
  const group = useRef<THREE.Group>(null);
  useFrame((_, dt) => {
    if (group.current) group.current.rotation.y += dt * 0.08;
  });
  return (
    <group ref={group}>
      <mesh>
        <icosahedronGeometry args={[1.15, 1]} />
        <meshBasicMaterial
          color="#00E5FF"
          wireframe
          transparent
          opacity={0.35}
        />
      </mesh>
      <mesh>
        <icosahedronGeometry args={[1.15, 1]} />
        <meshStandardMaterial
          color="#0a2530"
          emissive="#00E5FF"
          emissiveIntensity={0.15}
          roughness={0.35}
          metalness={0.6}
          transparent
          opacity={0.18}
        />
      </mesh>
    </group>
  );
}

function ParticleStream({
  verdictRatio,
}: {
  verdictRatio: { pass: number; warn: number; crit: number };
}) {
  const count = 160;
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  const particles = useMemo(() => {
    const arr = [];
    const kinds: (keyof typeof COLORS)[] = [];
    const nPass = Math.round(count * verdictRatio.pass);
    const nWarn = Math.round(count * verdictRatio.warn);
    for (let i = 0; i < count; i++) {
      kinds.push(i < nPass ? "pass" : i < nPass + nWarn ? "warn" : "crit");
    }
    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 4.4 + Math.random() * 2.2;
      arr.push({
        start: new THREE.Vector3(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.sin(phi) * Math.sin(theta),
          r * Math.cos(phi)
        ),
        speed: 0.12 + Math.random() * 0.18,
        offset: Math.random() * 10,
        kind: kinds[i],
        exitTheta: Math.random() * Math.PI * 2,
      });
    }
    return arr;
  }, [verdictRatio]);

  // 顏色是每顆粒子固定的屬性,掛載時設一次即可,不必每個 frame 重寫。
  useEffect(() => {
    if (!meshRef.current) return;
    particles.forEach((p, i) => meshRef.current!.setColorAt(i, COLORS[p.kind]));
    if (meshRef.current.instanceColor) meshRef.current.instanceColor.needsUpdate = true;
  }, [particles]);

  const scratchPos = useMemo(() => new THREE.Vector3(), []);
  const scratchDir = useMemo(() => new THREE.Vector3(), []);
  const skip = useRef(0);

  useFrame((state) => {
    // 慢速漂移的動畫不需要每個 rAF 都重算——隔一幀更新一次,肉眼看不出差異,
    // 但主執行緒工作量直接減半。
    skip.current = (skip.current + 1) % 2;
    if (skip.current !== 0) return;

    const t = state.clock.elapsedTime;
    particles.forEach((p, i) => {
      const local = (t * p.speed + p.offset) % 6.5;
      if (local < 4) {
        // 湧向核心
        scratchPos.copy(p.start).multiplyScalar(1 - local / 4.2);
      } else {
        // 命中核心後,依結論分流射出
        const k = (local - 4) / 2.5;
        scratchDir
          .set(
            Math.cos(p.exitTheta),
            p.kind === "pass" ? 0.6 : p.kind === "warn" ? 0.05 : -0.6,
            Math.sin(p.exitTheta)
          )
          .normalize();
        scratchPos.copy(scratchDir).multiplyScalar(k * 5.5);
      }
      dummy.position.copy(scratchPos);
      const s = local < 4 ? 0.045 : 0.045 * (1 - (local - 4) / 2.5);
      dummy.scale.setScalar(Math.max(s, 0.008));
      dummy.updateMatrix();
      meshRef.current?.setMatrixAt(i, dummy.matrix);
    });
    if (meshRef.current) meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[1, 6, 6]} />
      <meshBasicMaterial toneMapped={false} />
    </instancedMesh>
  );
}

function ParallaxRig({ children }: { children: React.ReactNode }) {
  const group = useRef<THREE.Group>(null);
  const mouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      mouse.current = {
        x: e.clientX / window.innerWidth - 0.5,
        y: e.clientY / window.innerHeight - 0.5,
      };
    };
    window.addEventListener("pointermove", onMove, { passive: true });
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  useFrame(() => {
    if (!group.current) return;
    group.current.rotation.y += (mouse.current.x * 0.35 - group.current.rotation.y) * 0.02;
    group.current.rotation.x += (-mouse.current.y * 0.2 - group.current.rotation.x) * 0.02;
  });

  return <group ref={group}>{children}</group>;
}

// 靜態替代:純漸層球,不跑任何 3D 運算。prefers-reduced-motion 與
// WebGL 初始化失敗共用同一個回退,兩者的意圖其實是同一件事——
// 「這台裝置/這個瀏覽器不該跑這段動畫」。
function StaticFallback() {
  return (
    <div
      aria-hidden
      className="h-full w-full rounded-full opacity-60"
      style={{
        background:
          "radial-gradient(circle at 50% 45%, rgba(0,229,255,0.25), transparent 60%)",
      }}
    />
  );
}

export default function AuditCoreScene({
  verdictRatio,
}: {
  verdictRatio: { pass: number; warn: number; crit: number };
}) {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  if (reduced) return <StaticFallback />;

  return (
    <SceneErrorBoundary fallback={<StaticFallback />}>
      <Canvas
        dpr={[1, 1.2]}
        camera={{ position: [0, 0, 6.4], fov: 42 }}
        gl={{ antialias: false, alpha: true, failIfMajorPerformanceCaveat: false, powerPreference: "low-power" }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener(
            "webglcontextlost",
            (e) => e.preventDefault(),
            false
          );
        }}
      >
        <ambientLight intensity={0.4} />
        <pointLight position={[4, 4, 4]} intensity={1.1} color="#00E5FF" />
        <pointLight position={[-4, -3, -2]} intensity={0.6} color="#9A7BFF" />
        <ParallaxRig>
          <Core />
          <ParticleStream verdictRatio={verdictRatio} />
        </ParallaxRig>
      </Canvas>
    </SceneErrorBoundary>
  );
}
