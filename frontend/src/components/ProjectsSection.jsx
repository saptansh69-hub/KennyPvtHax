import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Check, Crown } from "lucide-react";
import { projects } from "../mock";

const ProjectsSection = () => {
  const navigate = useNavigate();

  return (
    <section id="projects" className="relative border-t border-zinc-800/80 py-20 md:py-28">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">catalog</p>
            <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">
              Three builds. <span className="text-red-500">One arsenal.</span>
            </h2>
          </div>
          <p className="max-w-md text-sm text-zinc-500">
            Every project is engineered for a different kind of player — from the market standard to a demonstration of pure power.
          </p>
        </div>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {projects.map((p, idx) => (
            <div
              key={p.id}
              className="tech-card group relative flex flex-col overflow-hidden"
              style={{ animation: `float-up 0.6s ease ${idx * 0.1}s both` }}
            >
              <div className="relative h-52 overflow-hidden bg-black">
                <img
                  src={p.image}
                  alt={p.name}
                  className="h-full w-full object-contain p-6 transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 via-transparent to-transparent" />
                <div className="absolute left-4 top-4 flex items-center gap-2">
                  <span className="font-mono2 text-xs text-zinc-400">/ {p.code}</span>
                  {p.hasAdmin && (
                    <span className="inline-flex items-center gap-1 border border-red-600/60 bg-red-600/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-red-300">
                      <Crown className="h-3 w-3" /> Elite
                    </span>
                  )}
                </div>
                <div className="absolute bottom-4 left-4">
                  <h3 className="font-display text-2xl font-bold text-white">{p.name}</h3>
                  <p className="font-mono2 text-xs text-red-400">{p.tagline}</p>
                </div>
              </div>

              <div className="flex flex-1 flex-col p-6">
                <p className="text-sm leading-relaxed text-zinc-400">{p.description}</p>
                <ul className="mt-5 space-y-2.5">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-zinc-300">
                      <Check className="h-4 w-4 shrink-0 text-red-500" />
                      {f}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => navigate("/pricing")}
                  className="mt-6 inline-flex items-center justify-between border border-zinc-700 bg-zinc-800/50 px-4 py-3 text-sm font-semibold text-white transition-colors hover:border-red-600/60 hover:bg-red-600/10 clip-corner"
                >
                  View pricing
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
              </div>
              <span
                className="absolute inset-x-0 bottom-0 h-0.5 origin-left scale-x-0 transition-transform duration-300 group-hover:scale-x-100"
                style={{ background: p.accent }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProjectsSection;
