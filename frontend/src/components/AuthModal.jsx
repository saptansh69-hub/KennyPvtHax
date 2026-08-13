import React, { useState } from "react";
import { X, Mail, Send, Lock, User, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../hooks/use-toast";

const AuthModal = ({ open, onClose, onSuccess }) => {
  const { login, signup } = useAuth();
  const { toast } = useToast();
  const [mode, setMode] = useState("login"); // login | signup
  const [method, setMethod] = useState("email"); // email | telegram
  const [form, setForm] = useState({ name: "", email: "", telegram: "", password: "", identifier: "" });
  const [busy, setBusy] = useState(false);

  if (!open) return null;

  const upd = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      if (mode === "signup") {
        const payload = {
          name: form.name,
          password: form.password,
          ...(method === "email" ? { email: form.email } : { telegram: form.telegram }),
        };
        await signup(payload);
        toast({ title: "Welcome to KennyPvtHax", description: "Your account is ready." });
      } else {
        await login({ identifier: form.identifier, password: form.password });
        toast({ title: "Signed in", description: "Good to see you back." });
      }
      onSuccess?.();
      onClose();
    } catch (err) {
      toast({ title: "Something went wrong", description: err?.response?.data?.detail || "Please try again." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md border border-red-900/50 bg-zinc-950 p-7 clip-corner">
        <div className="grid-bg absolute inset-0 opacity-30" />
        <button onClick={onClose} className="absolute right-4 top-4 z-10 text-zinc-500 hover:text-white">
          <X className="h-5 w-5" />
        </button>
        <div className="relative">
          <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Kenny system / access</p>
          <h2 className="mt-2 font-display text-2xl font-bold">
            {mode === "login" ? "Sign in" : "Join the community"}
          </h2>
          <p className="mt-1 text-sm text-zinc-500">
            {mode === "login" ? "Access your keys and purchases." : "Create an account to track your keys."}
          </p>

          <form onSubmit={submit} className="mt-6 space-y-4">
            {mode === "signup" && (
              <>
                <div className="flex items-center border border-zinc-800 bg-zinc-900/60 focus-within:border-red-600/60">
                  <span className="px-3 text-zinc-500"><User className="h-4 w-4" /></span>
                  <input value={form.name} onChange={upd("name")} required placeholder="Display name"
                    className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600" />
                </div>
                <div className="inline-flex w-full border border-zinc-800 bg-zinc-900/60 p-1">
                  {[["email", "Email"], ["telegram", "Telegram"]].map(([id, lbl]) => (
                    <button type="button" key={id} onClick={() => setMethod(id)}
                      className={`flex-1 py-1.5 text-xs font-semibold font-mono2 ${method === id ? "bg-red-600 text-white" : "text-zinc-400"}`}>
                      {lbl}
                    </button>
                  ))}
                </div>
                {method === "email" ? (
                  <div className="flex items-center border border-zinc-800 bg-zinc-900/60 focus-within:border-red-600/60">
                    <span className="px-3 text-zinc-500"><Mail className="h-4 w-4" /></span>
                    <input type="email" value={form.email} onChange={upd("email")} required placeholder="you@email.com"
                      className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600" />
                  </div>
                ) : (
                  <div className="flex items-center border border-zinc-800 bg-zinc-900/60 focus-within:border-red-600/60">
                    <span className="px-3 text-zinc-500"><Send className="h-4 w-4" /></span>
                    <input value={form.telegram} onChange={upd("telegram")} required placeholder="@yourusername"
                      className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600" />
                  </div>
                )}
              </>
            )}

            {mode === "login" && (
              <div className="flex items-center border border-zinc-800 bg-zinc-900/60 focus-within:border-red-600/60">
                <span className="px-3 text-zinc-500"><User className="h-4 w-4" /></span>
                <input value={form.identifier} onChange={upd("identifier")} required placeholder="Email or @telegram"
                  className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600" />
              </div>
            )}

            <div className="flex items-center border border-zinc-800 bg-zinc-900/60 focus-within:border-red-600/60">
              <span className="px-3 text-zinc-500"><Lock className="h-4 w-4" /></span>
              <input type="password" value={form.password} onChange={upd("password")} required placeholder="Password"
                className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600" />
            </div>

            <button type="submit" disabled={busy}
              className="inline-flex w-full items-center justify-center gap-2 bg-red-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-500 disabled:opacity-60 clip-corner">
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              {mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-zinc-500">
            {mode === "login" ? "New here? " : "Already have an account? "}
            <button onClick={() => setMode(mode === "login" ? "signup" : "login")} className="font-semibold text-red-400 hover:text-red-300">
              {mode === "login" ? "Create an account" : "Sign in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
