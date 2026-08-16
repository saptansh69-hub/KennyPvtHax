import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Flame, Timer } from "lucide-react";
import { promo } from "../mock";
import { promoActive, timeLeft, pad } from "../utils/promo";

const PromoBanner = () => {
  const navigate = useNavigate();
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  if (!promoActive(now)) return null;
  const { d, h, m, s } = timeLeft(now);

  const Box = ({ v, l }) => (
    <div className="flex flex-col items-center">
      <span className="min-w-[2.2rem] border border-red-500/40 bg-black/40 px-1.5 py-0.5 font-mono2 text-sm font-bold text-white">{pad(v)}</span>
      <span className="mt-0.5 font-mono2 text-[8px] uppercase tracking-widest text-red-100/70">{l}</span>
    </div>
  );

  return (
    <button
      onClick={() => navigate("/pricing")}
      className="group relative block w-full overflow-hidden border-b border-red-500/40 bg-gradient-to-r from-red-700 via-red-600 to-red-700 text-white"
    >
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-x-4 gap-y-1.5 px-4 py-2 text-center">
        <span className="inline-flex items-center gap-2 font-display text-sm font-bold tracking-wide">
          <Flame className="h-4 w-4 animate-flicker" /> {promo.label}
        </span>
        <span className="hidden text-sm text-red-50/90 sm:inline">
          OG &amp; Frozen Fire from <b className="text-white">₹69</b> — grab a key before it ends
        </span>
        <span className="inline-flex items-center gap-2">
          <Timer className="h-4 w-4 text-red-100" />
          <span className="flex items-center gap-1.5">
            <Box v={d} l="days" /><Box v={h} l="hrs" /><Box v={m} l="min" /><Box v={s} l="sec" />
          </span>
        </span>
      </div>
    </button>
  );
};

export default PromoBanner;
