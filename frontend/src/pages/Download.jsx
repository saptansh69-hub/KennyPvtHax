import React from "react";
import { useNavigate } from "react-router-dom";
import { Download as DownloadIcon, Send, Smartphone, ShieldCheck, KeyRound } from "lucide-react";
import { serverStatus, telegramUrl } from "../mock";

const steps = [
  { code: "01", title: "Buy a key", desc: "Choose your product and duration on the pricing page, then check out with UPI or card." },
  { code: "02", title: "Get it on Telegram", desc: "Your key is generated instantly and delivered to your Telegram username." },
  { code: "03", title: "Download", desc: "Grab the latest build below." },
  { code: "04", title: "Activate", desc: "Enter your key to activate." },
];

// Each entry: { name, tag, size }
const builds = [];

const Download = () => {
  const navigate = useNavigate();
  return (
    <div className="relative">
      <div className="radial-red absolute inset-x-0 top-0 h-72" />
      <div className="relative mx-auto max-w-5xl px-6 py-16 md:py-24">
        <div className="text-center">
          <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Download / loader</p>
          <h1 className="mt-3 font-display text-4xl font-bold tracking-tight md:text-6xl">
            Get the latest <span className="text-red-500">build.</span>
          </h1>
          <div className="mt-5 inline-flex items-center gap-3 border border-zinc-800 bg-zinc-900/60 px-4 py-2 font-mono2 text-xs">
            <span className="live-dot inline-block h-2 w-2 rounded-full bg-green-400" />
            <span className="text-green-400">{serverStatus.status}</span>
            {serverStatus.version && <span className="text-zinc-500">· {serverStatus.version}</span>}
          </div>
        </div>

        {builds.length > 0 && (
        <div className="mt-12 grid gap-4 sm:grid-cols-2">
          {builds.map((b) => (
            <div key={b.name} className="flex items-center justify-between border border-zinc-800 bg-zinc-900/40 p-5 clip-corner">
              <div className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center border border-red-600/50 bg-red-600/10">
                  <Smartphone className="h-5 w-5 text-red-500" />
                </span>
                <div>
                  <p className="font-display font-bold text-white">{b.name}</p>
                  <p className="font-mono2 text-xs text-zinc-500">{b.tag} · {b.size}</p>
                </div>
              </div>
              <button
                onClick={() => navigate("/pricing")}
                className="inline-flex items-center gap-2 bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner"
              >
                <DownloadIcon className="h-4 w-4" /> Get
              </button>
            </div>
          ))}
        </div>
        )}

        <div className="mt-6 flex items-center gap-3 border border-red-900/40 bg-red-950/20 p-4 text-sm text-zinc-400 clip-corner">
          <KeyRound className="h-5 w-5 shrink-0 text-red-500" />
          A valid key is required. No key yet? Grab one from pricing — it arrives on Telegram instantly.
        </div>

        <div className="mt-16">
          <h2 className="font-display text-2xl font-bold md:text-3xl">How it works</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((s) => (
              <div key={s.code} className="border-l-2 border-red-600/50 pl-4">
                <span className="font-mono2 text-sm text-red-500">{s.code}</span>
                <h3 className="mt-1 font-display text-lg font-bold text-white">{s.title}</h3>
                <p className="mt-1 text-sm text-zinc-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 flex flex-col items-center gap-4 border border-zinc-800 bg-zinc-900/40 p-8 text-center clip-corner">
          <ShieldCheck className="h-8 w-8 text-red-500" />
          <h3 className="font-display text-xl font-bold">Need help with setup?</h3>
          <p className="max-w-md text-sm text-zinc-500">Our team is on Telegram around the clock for keys, installation and troubleshooting.</p>
          <a
            href={telegramUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 border border-red-600/50 bg-red-600/10 px-6 py-3 text-sm font-semibold text-red-300 hover:bg-red-600/20 transition-colors clip-corner"
          >
            <Send className="h-4 w-4" /> Open Telegram
          </a>
        </div>
      </div>
    </div>
  );
};

export default Download;
