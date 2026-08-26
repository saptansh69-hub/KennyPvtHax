import React, { useEffect, useState } from "react";
import { serverStatus } from "../mock";
import { ShieldCheck, Activity } from "lucide-react";

const formatPatch = (iso) => {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
};

const StatusBar = () => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  const items = [
    { icon: null, node: (
      <span className="flex items-center gap-2">
        <span className="live-dot inline-block h-2 w-2 rounded-full bg-green-400" />
        <span className="text-green-400 font-semibold">{serverStatus.status}</span>
        <span className="text-zinc-500">· {serverStatus.statusLabel}</span>
      </span>
    )},
    { node: (
      <span className="flex items-center gap-1.5">
        <ShieldCheck className="h-3.5 w-3.5 text-red-500" />
        <span className="text-zinc-400">Undetected</span>
      </span>
    )},
    { node: <span className="text-zinc-400">Build <span className="text-zinc-200">{serverStatus.version}</span></span> },
    { node: <span className="text-zinc-400">Last patch <span className="text-zinc-200">{formatPatch(serverStatus.lastPatch)} UTC</span></span> },
    { node: (
      <span className="flex items-center gap-1.5">
        <Activity className="h-3.5 w-3.5 text-red-500" />
        <span className="text-zinc-200">{serverStatus.activeUsers.toLocaleString()}</span>
        <span className="text-zinc-400">online</span>
      </span>
    )},
    { node: <span className="text-zinc-500 font-mono2">{new Date(now).toLocaleTimeString("en-GB")}</span> },
  ];

  return (
    <div className="w-full border-b border-red-900/40 bg-black/80 backdrop-blur text-[11px] md:text-xs font-mono2 tracking-wide overflow-hidden">
      {/* Desktop static row */}
      <div className="hidden md:flex mx-auto max-w-7xl items-center justify-between px-6 py-2">
        <div className="flex items-center gap-6">{items.slice(0, 4).map((it, i) => <div key={i}>{it.node}</div>)}</div>
        <div className="flex items-center gap-6">{items.slice(4).map((it, i) => <div key={i}>{it.node}</div>)}</div>
      </div>
      {/* Mobile marquee */}
      <div className="md:hidden py-2 whitespace-nowrap">
        <div className="animate-marquee inline-flex items-center gap-8 px-4">
          {[...items, ...items].map((it, i) => <div key={i}>{it.node}</div>)}
        </div>
      </div>
    </div>
  );
};

export default StatusBar;
