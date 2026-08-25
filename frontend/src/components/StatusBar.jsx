import React, { useEffect, useState } from "react";
import { serverStatus } from "../mock";
import { Activity } from "lucide-react";

const formatUpdate = (iso) => {
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

  const left = [
    (
      <span className="flex items-center gap-2">
        <span className="live-dot inline-block h-2 w-2 rounded-full bg-green-400" />
        <span className="text-green-400 font-semibold">{serverStatus.status}</span>
        <span className="text-zinc-500">· {serverStatus.statusLabel}</span>
      </span>
    ),
    serverStatus.version && (
      <span className="text-zinc-400">Build <span className="text-zinc-200">{serverStatus.version}</span></span>
    ),
    serverStatus.lastUpdate && (
      <span className="text-zinc-400">Last update <span className="text-zinc-200">{formatUpdate(serverStatus.lastUpdate)} UTC</span></span>
    ),
  ].filter(Boolean);

  const right = [
    serverStatus.activeUsers > 0 && (
      <span className="flex items-center gap-1.5">
        <Activity className="h-3.5 w-3.5 text-red-500" />
        <span className="text-zinc-200">{serverStatus.activeUsers.toLocaleString()}</span>
        <span className="text-zinc-400">online</span>
      </span>
    ),
    <span className="text-zinc-500 font-mono2">{new Date(now).toLocaleTimeString("en-GB")}</span>,
  ].filter(Boolean);

  const all = [...left, ...right];

  return (
    <div className="w-full border-b border-red-900/40 bg-black/80 backdrop-blur text-[11px] md:text-xs font-mono2 tracking-wide overflow-hidden">
      {/* Desktop static row */}
      <div className="hidden md:flex mx-auto max-w-7xl items-center justify-between px-6 py-2">
        <div className="flex items-center gap-6">{left.map((node, i) => <div key={i}>{node}</div>)}</div>
        <div className="flex items-center gap-6">{right.map((node, i) => <div key={i}>{node}</div>)}</div>
      </div>
      {/* Mobile marquee */}
      <div className="md:hidden py-2 whitespace-nowrap">
        <div className="animate-marquee inline-flex items-center gap-8 px-4">
          {[...all, ...all].map((node, i) => <div key={i}>{node}</div>)}
        </div>
      </div>
    </div>
  );
};

export default StatusBar;
