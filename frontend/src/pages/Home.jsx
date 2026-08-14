import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, KeyRound, Send, Cpu, ShieldCheck, Radio, Video } from "lucide-react";
import { coreFeatures, showcaseStats, telegramUrl, heroBgVideo } from "../mock";
import { toYouTubeBg } from "../utils/youtube";
import ProjectsSection from "../components/ProjectsSection";
import DemosSection from "../components/DemosSection";
import FeedbackSection from "../components/FeedbackSection";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div>
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="yt-bg">
          <iframe
            src={toYouTubeBg(heroBgVideo)}
            title="Cyberpunk background"
            allow="autoplay; encrypted-media"
            tabIndex={-1}
            aria-hidden="true"
          />
        </div>
        <div className="hero-video-overlay" />
        <div className="grid-bg absolute inset-0 opacity-30" />
        <div className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pb-32 md:pt-28">
          <div className="animate-float-up">
            <img src="/kenny-logo.jpg" alt="KennyPvtHax" className="h-14 w-14 rounded-lg border border-red-600/50 object-cover shadow-lg shadow-red-900/40" />
            <h1 className="mt-5 font-display text-5xl font-bold leading-[0.9] tracking-tight md:text-7xl lg:text-8xl">
              <span className="name-wrap"><span className="animated-name">KennyPvtHax</span></span>
            </h1>
            <p className="mt-6 font-tech text-lg text-zinc-400 md:text-2xl">
              Kernel-level capability for PUBGM &amp; BGMI. Stable operation. Instant delivery.
            </p>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-zinc-500 md:text-base">
              Premium plugins engineered to run in the system kernel while you stay in control at the interface. Undetected, stream-safe and updated within hours of every patch.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <button
                onClick={() => navigate("/pricing")}
                className="group inline-flex items-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-red-500 clip-corner"
              >
                <KeyRound className="h-4 w-4" /> Get your key
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
                className="tech-card group p-5 clip-corner"
                style={{ animation: `float-up 0.6s ease ${0.2 + i * 0.08}s both` }}
              >
                <span className="grid h-10 w-10 place-items-center border border-red-600/40 bg-red-600/10 transition-colors group-hover:bg-red-600/20">
                  <s.icon className="h-5 w-5 text-red-500" />
                </span>
                <p className="mt-4 font-mono2 text-[11px] uppercase tracking-widest text-zinc-500">{s.label}</p>
                <p className="mt-1 font-display text-xl font-bold text-white">{s.value}</p>
                <p className="text-xs text-zinc-500">{s.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROJECTS */}
      <ProjectsSection />

      {/* PER-PROJECT DEMOS */}
      <DemosSection />

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

          <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {coreFeatures.map((f, i) => (
              <div key={f.code} className="tech-card group p-8 clip-corner" style={{ animation: `float-up 0.6s ease ${i * 0.06}s both` }}>
                <div className="flex items-center justify-between">
                  <span className="font-display text-3xl font-bold text-red-600/30 transition-colors group-hover:text-red-600/70">{f.code}</span>
                  <span className="h-1.5 w-1.5 rounded-full bg-red-600 opacity-40 transition-opacity group-hover:opacity-100" />
                </div>
                <h3 className="mt-4 font-display text-xl font-bold text-white">{f.title}</h3>
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

      {/* FEEDBACK */}
      <FeedbackSection />

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
