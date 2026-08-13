import React from "react";
import { Link } from "react-router-dom";
import { Zap, Send } from "lucide-react";
import { navLinks, telegramHandle, telegramUrl } from "../mock";

const Footer = () => {
  return (
    <footer className="relative border-t border-zinc-800/80 bg-black">
      <div className="grid-bg absolute inset-0 opacity-40" />
      <div className="relative mx-auto max-w-7xl px-6 py-14">
        <div className="grid gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2">
              <span className="grid h-8 w-8 place-items-center border border-red-600/60 bg-red-600/10 clip-corner">
                <Zap className="h-4 w-4 text-red-500" fill="currentColor" />
              </span>
              <span className="font-display text-lg font-bold">
                Kenny<span className="text-red-500">PvtHax</span>
              </span>
            </div>
            <p className="mt-4 max-w-sm text-sm text-zinc-500">
              Premium PUBG Mobile & BGMI plugins. Kernel-level capability, stable operation and instant key delivery via Telegram.
            </p>
            <a
              href={telegramUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-5 inline-flex items-center gap-2 border border-red-600/50 bg-red-600/10 px-4 py-2 text-sm font-semibold text-red-400 hover:bg-red-600/20 transition-colors clip-corner"
            >
              <Send className="h-4 w-4" /> {telegramHandle}
            </a>
          </div>

          <div>
            <h4 className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Navigate</h4>
            <ul className="mt-4 space-y-2.5">
              {navLinks.map((l) => (
                <li key={l.label}>
                  <Link to={l.to.startsWith("/#") ? "/" : l.to} className="text-sm text-zinc-400 hover:text-red-400 transition-colors">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Legal</h4>
            <ul className="mt-4 space-y-2.5 text-sm text-zinc-400">
              <li>Terms of Service</li>
              <li>Refund Policy</li>
              <li>Fair Use</li>
              <li className="text-zinc-600">For demonstration & entertainment</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-zinc-800/80 pt-6 md:flex-row">
          <p className="font-mono2 text-xs text-zinc-600">© {new Date().getFullYear()} KennyPvtHax · Kernel system / 01</p>
          <p className="font-mono2 text-xs text-zinc-600">Built for PUBGM & BGMI</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
