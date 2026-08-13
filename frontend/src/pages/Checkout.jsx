import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Trash2, ShoppingCart, Send, CreditCard, Smartphone, ArrowRight, CheckCircle2, ShieldCheck } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useToast } from "../hooks/use-toast";

const Checkout = () => {
  const { items, removeItem, totalInr, totalUsd, clearCart } = useCart();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [currency, setCurrency] = useState("inr");
  const [method, setMethod] = useState("upi");
  const [telegram, setTelegram] = useState("");
  const [email, setEmail] = useState("");
  const [placed, setPlaced] = useState(false);

  const total = currency === "inr" ? `₹${totalInr}` : `$${totalUsd}`;

  const handlePlace = (e) => {
    e.preventDefault();
    if (!telegram.trim()) {
      toast({ title: "Telegram username required", description: "We deliver your key on Telegram." });
      return;
    }
    // Frontend-only mock: pretend payment succeeded
    setPlaced(true);
    clearCart();
  };

  if (placed) {
    return (
      <div className="mx-auto max-w-lg px-6 py-24 text-center">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-full border border-green-600/50 bg-green-600/10">
          <CheckCircle2 className="h-8 w-8 text-green-400" />
        </div>
        <h1 className="mt-6 font-display text-3xl font-bold">Order placed</h1>
        <p className="mt-3 text-sm text-zinc-500">
          Your key will be delivered to <span className="text-red-400">{telegram}</span> on Telegram shortly.
        </p>
        <div className="mt-4 inline-block border border-yellow-600/40 bg-yellow-950/20 px-4 py-2 font-mono2 text-xs text-yellow-500/90">
          Demo checkout — payment & delivery are mocked for now
        </div>
        <div className="mt-8">
          <button onClick={() => navigate("/")} className="inline-flex items-center gap-2 bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner">
            Back home <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-6 py-24 text-center">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-full border border-zinc-700 bg-zinc-900">
          <ShoppingCart className="h-7 w-7 text-zinc-500" />
        </div>
        <h1 className="mt-6 font-display text-2xl font-bold">Your cart is empty</h1>
        <p className="mt-2 text-sm text-zinc-500">Add a key from the pricing page to continue.</p>
        <button onClick={() => navigate("/pricing")} className="mt-6 inline-flex items-center gap-2 bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner">
          Browse pricing <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Checkout / secure</p>
      <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">Complete your order</h1>

      <div className="mt-10 grid gap-8 lg:grid-cols-5">
        {/* Order summary */}
        <div className="lg:col-span-2">
          <div className="border border-zinc-800 bg-zinc-900/40 p-6 clip-corner">
            <div className="flex items-center justify-between">
              <h2 className="font-display text-lg font-bold">Your cart</h2>
              <div className="inline-flex border border-zinc-800 bg-zinc-950 p-0.5 text-xs font-mono2">
                {["inr", "usd"].map((c) => (
                  <button key={c} onClick={() => setCurrency(c)} className={`px-2.5 py-1 ${currency === c ? "bg-red-600 text-white" : "text-zinc-400"}`}>
                    {c.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {items.map((it) => (
                <div key={it.key} className="flex items-center justify-between border-b border-zinc-800 pb-3">
                  <div>
                    <p className="text-sm font-semibold text-white">{it.project}</p>
                    <p className="font-mono2 text-xs text-zinc-500">{it.plan} · {it.duration}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-display text-sm font-bold text-white">{currency === "inr" ? `₹${it.inr}` : `$${it.usd}`}</span>
                    <button onClick={() => removeItem(it.key)} className="text-zinc-500 hover:text-red-500 transition-colors">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 flex items-center justify-between">
              <span className="font-mono2 text-sm uppercase tracking-widest text-zinc-500">Total</span>
              <span className="font-display text-2xl font-bold text-red-500">{total}</span>
            </div>
          </div>
        </div>

        {/* Payment form */}
        <div className="lg:col-span-3">
          <form onSubmit={handlePlace} className="border border-zinc-800 bg-zinc-900/40 p-6 clip-corner">
            <h2 className="font-display text-lg font-bold">Delivery details</h2>
            <div className="mt-4 grid gap-4">
              <label className="block">
                <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Telegram username *</span>
                <div className="mt-1.5 flex items-center border border-zinc-800 bg-zinc-950 focus-within:border-red-600/60">
                  <span className="px-3 text-zinc-500"><Send className="h-4 w-4" /></span>
                  <input
                    value={telegram}
                    onChange={(e) => setTelegram(e.target.value)}
                    placeholder="@yourusername"
                    className="w-full bg-transparent py-2.5 pr-3 text-sm text-white outline-none placeholder:text-zinc-600"
                  />
                </div>
              </label>
              <label className="block">
                <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Email (optional)</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@email.com"
                  className="mt-1.5 w-full border border-zinc-800 bg-zinc-950 px-3 py-2.5 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-red-600/60"
                />
              </label>
            </div>

            <h2 className="mt-7 font-display text-lg font-bold">Payment method</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {[
                { id: "upi", label: "UPI", sub: "GPay / PhonePe / Paytm", icon: Smartphone },
                { id: "stripe", label: "Card", sub: "Stripe · Visa / Mastercard", icon: CreditCard },
              ].map((m) => (
                <button
                  type="button"
                  key={m.id}
                  onClick={() => setMethod(m.id)}
                  className={`flex items-center gap-3 border p-4 text-left transition-colors clip-corner ${
                    method === m.id ? "border-red-600/70 bg-red-600/10" : "border-zinc-800 bg-zinc-950 hover:border-zinc-700"
                  }`}
                >
                  <m.icon className={`h-5 w-5 ${method === m.id ? "text-red-500" : "text-zinc-500"}`} />
                  <div>
                    <p className="text-sm font-semibold text-white">{m.label}</p>
                    <p className="font-mono2 text-[11px] text-zinc-500">{m.sub}</p>
                  </div>
                </button>
              ))}
            </div>

            <button type="submit" className="mt-7 inline-flex w-full items-center justify-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner">
              Pay {total} <ArrowRight className="h-4 w-4" />
            </button>
            <p className="mt-3 flex items-center justify-center gap-1.5 font-mono2 text-[11px] text-zinc-600">
              <ShieldCheck className="h-3.5 w-3.5" /> Payment is mocked in this preview
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
