import React from "react";
import { useNavigate } from "react-router-dom";
import { coreFeatures, projects } from "../mock";
import { Check, ArrowRight, Cpu, Layers, Eye, Shield } from "lucide-react";

const layers = [
  { code: "01", group: "Hardware layer", title: "Hardware bullet tracking", desc: "Trajectory tracking computed at the hardware layer for pixel-accurate aim.", icon: Cpu },
  { code: "02", group: "JOLT check", title: "Jolt obstacle check", desc: "Collision state detection so shots respect real geometry.", icon: Shield },
  { code: "03", group: "Display layer", title: "Stream mode", desc: "Stream concealment hides overlays while recording.", icon: Eye },
  { code: "04", group: "Kernel layer", title: "Kernel capability", desc: "Core capabilities run inside the system kernel for stability.", icon: Layers },
];

const Features = () => {
  const navigate = useNavigate();
  return (
    <div className="relative">
      <div className="grid-bg absolute inset-x-0 top-0 h-96 opacity-50" />
      <div className="relative mx-auto max-w-7xl px-6 py-16 md:py-24">
        <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">KC / core capabilities</p>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight md:text-6xl">
          Every layer, <span className="text-red-500">weaponised.</span>
        </h1>
        <p className="mt-4 max-w-xl text-sm text-zinc-500">
          From the hardware layer to the kernel, each stage of the runtime is tuned for stability, stealth and control.
        </p>

        <div className="mt-14 grid gap-6 md:grid-cols-2">
          {layers.map((l) => (
            <div key={l.code} className="group relative border border-zinc-800 bg-zinc-900/40 p-8 transition-colors hover:border-red-600/60 clip-corner">
              <div className="flex items-center justify-between">
                <span className="grid h-10 w-10 place-items-center border border-red-600/50 bg-red-600/10">
                  <l.icon className="h-5 w-5 text-red-500" />
                </span>
                <span className="font-mono2 text-xs text-zinc-500">/ {l.code}</span>
              </div>
              <p className="mt-5 font-mono2 text-[11px] uppercase tracking-widest text-zinc-500">{l.group}</p>
              <h3 className="mt-1 font-display text-2xl font-bold text-white">{l.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500">{l.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-20">
          <h2 className="font-display text-2xl font-bold md:text-3xl">Included with every build</h2>
          <div className="mt-8 grid gap-px overflow-hidden border border-zinc-800 bg-zinc-800 sm:grid-cols-2 lg:grid-cols-3">
            {coreFeatures.map((f) => (
              <div key={f.code} className="bg-zinc-950 p-8 transition-colors hover:bg-zinc-900">
                <Check className="h-5 w-5 text-red-500" />
                <h3 className="mt-3 font-display text-lg font-bold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-zinc-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-20 grid gap-6 md:grid-cols-3">
          {projects.map((p) => (
            <div key={p.id} className="border border-zinc-800 bg-zinc-900/40 p-6 clip-corner">
              <h3 className="font-display text-xl font-bold text-white">{p.name}</h3>
              <p className="mt-1 font-mono2 text-xs text-red-400">{p.tagline}</p>
              <ul className="mt-4 space-y-2">
                {p.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-zinc-300">
                    <Check className="h-4 w-4 text-red-500" /> {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-16 flex justify-center">
          <button
            onClick={() => navigate("/pricing")}
            className="inline-flex items-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner"
          >
            See pricing <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Features;
