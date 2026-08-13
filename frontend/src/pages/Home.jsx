import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Download, Send, Video, Cpu, ShieldCheck, Radio } from "lucide-react";
import { coreFeatures, showcaseStats, telegramUrl } from "../mock";
import ProjectsSection from "../components/ProjectsSection";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="grid-bg absolute inset-0 opacity-60" />
        <div className="radial-red absolute inset-0" />
        <div className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pb-32 md:pt-28">
          <div className="animate-float-up">
            <p className="font-mono2 text-xs uppercase tracking-[0.3em] text-red-500">Kenny system / 01</p>
            <h1 className="mt-5 font-display text-5xl font-bold leading-[0.95] tracking-tight md:text-8xl">
              Kenny<span className="text-red-500 text-glow-red">PvtHax</span>
            </h1>
            <p className="mt-4 font-tech text-lg text-zinc-400 md:text-2xl">
              Kernel-level capability for PUBGM &amp; BGMI. Stable operation. Instant delivery.
            </p>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-zinc-500 md:text-base">
              Premium plugins engineered to run in the system kernel while you stay in control at the interface. Undetected, stream-safe and updated within hours of every patch.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <button
                onClick={() => navigate("/download")}
                className="group inline-flex items-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-red-500 clip-corner"
              >
                <Download className="h-4 w-4" /> Download now
              </button>
              <button
                onClick={() => navigate("/pricing")}
                className="group inline-flex items-center gap-2 border border-zinc-700 bg-zinc-900/50 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:border-red-600/60 clip-corner"
              >
                View pricing <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>
              <a
                href={telegramUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-2 py-3.5 text-sm font-semibold text-zinc-300 transition-colors hover:text-red-400"
              >
                <Send className="h-4 w-4" /> Join Telegram
              </a>
            </div>
          </div>

          {/* Runtime status card */}
          <div className="mt-16 grid gap-4 md:grid-cols-4">
            {[
              { icon: Cpu, label: "Kernel core", value: "Running", sub: "Stable status" },
              { icon: ShieldCheck, label: "Anti-cheat", value: "Bypassed", sub: "Evasion active" },
              { icon: Radio, label: "Stream mode", value: "Enabled", sub: "ESP concealed" },
              { icon: Video, label: "Display layer", value: "Clean", sub: "Overlay hidden" },
            ].map((s, i) => (
              <div
                key={s.label}
                className="relative border border-zinc-800 bg-zinc-900/50 p-5 scanline clip-corner"
                style={{ animation: `float-up 0.6s ease ${0.2 + i * 0.08}s both` }}
              >
                <s.icon className="h-5 w-5 text-red-500" />
                <p className="mt-3 font-mono2 text-[11px] uppercase tracking-widest text-zinc-500">{s.label}</p>
                <p className="mt-1 font-display text-xl font-bold text-white">{s.value}</p>
                <p className="text-xs text-zinc-500">{s.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROJECTS */}
      <ProjectsSection />

      {/* VIDEO SHOWCASE (placeholder, to be added later) */}
      <section className="relative border-t border-zinc-800/80 py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center">
            <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Gameplay / showcase</p>
            <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">See it in action</h2>
            <p className="mx-auto mt-4 max-w-lg text-sm text-zinc-500">
              A short gameplay reel to build trust with new players. Coming soon.
            </p>
          </div>
          <div className="mt-10 overflow-hidden border border-zinc-800 bg-zinc-900/40">
            <div className="relative flex aspect-video w-full items-center justify-center">
              <div className="grid-bg absolute inset-0 opacity-40" />
              <div className="radial-red absolute inset-0 opacity-70" />
              <div className="relative flex flex-col items-center">
                <span className="grid h-16 w-16 place-items-center rounded-full border border-red-600/60 bg-red-600/15">
                  <Video className="h-7 w-7 text-red-500" />
                </span>
                <p className="mt-4 font-tech text-lg text-zinc-300">Gameplay video coming soon</p>
                <p className="font-mono2 text-xs text-zinc-600">/ reel slot reserved</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CORE FEATURES */}
      <section className="relative border-t border-zinc-800/80 py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-end">
            <div>
              <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Core capabilities</p>
              <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">
                Control at the interface.<br />Run in the <span className="text-red-500">kernel.</span>
              </h2>
            </div>
            <button
              onClick={() => navigate("/features")}
              className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-300 hover:text-red-400 transition-colors"
            >
              View feature details <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          <div className="mt-14 grid gap-px overflow-hidden border border-zinc-800 bg-zinc-800 sm:grid-cols-2 lg:grid-cols-3">
            {coreFeatures.map((f) => (
              <div key={f.code} className="group bg-zinc-950 p-8 transition-colors hover:bg-zinc-900">
                <span className="font-mono2 text-sm text-red-500">{f.code}</span>
                <h3 className="mt-3 font-display text-xl font-bold text-white">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-500">{f.desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {showcaseStats.map((s) => (
              <div key={s.label} className="border-l-2 border-red-600/50 pl-4">
                <p className="font-display text-3xl font-bold text-white">{s.value}</p>
                <p className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden border-t border-zinc-800/80 py-20 md:py-28">
        <div className="radial-red absolute inset-0" />
        <div className="relative mx-auto max-w-3xl px-6 text-center">
          <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Ready to start</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">
            Get the latest KennyPvtHax build.
          </h2>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate("/pricing")}
              className="inline-flex items-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-red-500 clip-corner"
            >
              Buy a key <ArrowRight className="h-4 w-4" />
            </button>
            <a
              href={telegramUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 border border-zinc-700 bg-zinc-900/50 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:border-red-600/60 clip-corner"
            >
              <Send className="h-4 w-4" /> Join Telegram
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
