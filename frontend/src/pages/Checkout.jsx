import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Trash2, ShoppingCart, Send, CreditCard, Smartphone, ArrowRight, CheckCircle2, ShieldCheck, Loader2, Copy, Check, Clock } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useToast } from "../hooks/use-toast";
import { api } from "../services/api";
import { qrForAmount } from "../utils/promo";

const Checkout = () => {
  const { items, removeItem, totalInr, totalUsd, clearCart } = useCart();
  const { toast } = useToast();
  const navigate = useNavigate();

  const [currency, setCurrency] = useState("inr");
  const [method, setMethod] = useState("upi");
  const [telegram, setTelegram] = useState("");
  const [email, setEmail] = useState("");
  const [placed, setPlaced] = useState(false);
  const [busy, setBusy] = useState(false);
  const [order, setOrder] = useState(null);
  const [copied, setCopied] = useState("");
  const [paymentRef, setPaymentRef] = useState("");

  const total = currency === "inr" ? `₹${totalInr}` : `$${totalUsd}`;
  const qrSrc = qrForAmount(totalInr);

  const copyKey = (key) => {
    navigator.clipboard?.writeText(key);
    setCopied(key);
    setTimeout(() => setCopied(""), 1500);
  };

  const handlePlace = async (e) => {
    e.preventDefault();
    if (!telegram.trim()) {
      toast({ title: "Telegram username required", description: "We deliver your key on Telegram." });
      return;
    }
    if (method === "upi" && !paymentRef.trim()) {
      toast({ title: "Enter your UPI reference", description: "Paste the UTR / transaction ID after paying." });
      return;
    }
    setBusy(true);
    try {
      const payload = {
        telegram: telegram.trim(),
        email: email.trim() || undefined,
        method,
        currency,
        payment_ref: method === "upi" ? paymentRef.trim() : undefined,
        items: items.map((i) => ({
          projectId: i.projectId, project: i.project, planId: i.planId,
          plan: i.plan, duration: i.duration, inr: i.inr, usd: i.usd,
        })),
      };
      const res = await api.post("/orders", payload);
      setOrder(res.data);
      setPlaced(true);
      clearCart();
    } catch (err) {
      toast({ title: "Checkout failed", description: err?.response?.data?.detail || "Please try again." });
    } finally {
      setBusy(false);
    }
  };

  if (placed) {
    const pending = order?.status === "awaiting_verification";
    return (
      <div className="mx-auto max-w-xl px-6 py-20 text-center">
        <div className={`mx-auto grid h-16 w-16 place-items-center rounded-full border ${pending ? "border-yellow-600/50 bg-yellow-600/10" : "border-green-600/50 bg-green-600/10"}`}>
          {pending ? <Clock className="h-8 w-8 text-yellow-400" /> : <CheckCircle2 className="h-8 w-8 text-green-400" />}
        </div>
        <h1 className="mt-6 font-display text-3xl font-bold">{pending ? "Payment under verification" : "Order confirmed"}</h1>
        <p className="mt-3 text-sm text-zinc-500">
          {pending
            ? <>We're confirming your payment. Your key will be sent to <span className="text-red-400">{order?.telegram || telegram}</span> on Telegram the moment it's verified (usually within minutes).</>
            : <>Your key{order?.keys?.length > 1 ? "s" : ""} will be delivered to <span className="text-red-400">{order?.telegram || telegram}</span> on Telegram.</>}
        </p>

        {!pending && order?.keys?.length > 0 && (
          <div className="mt-6 space-y-2 text-left">
            {order.keys.map((k, i) => (
              <div key={i} className="flex flex-wrap items-center justify-between gap-3 border border-zinc-800 bg-zinc-950 p-3">
                <div>
                  <p className="text-sm font-semibold text-white">{k.project}</p>
                  <p className="font-mono2 text-xs text-zinc-500">{k.plan} · {k.duration}</p>
                </div>
                {k.key ? (
                  <button onClick={() => copyKey(k.key)}
                    className="inline-flex items-center gap-2 border border-red-900/50 bg-red-600/10 px-3 py-1.5 font-mono2 text-xs text-red-300 hover:bg-red-600/20 transition-colors">
                    {copied === k.key ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />} {k.key}
                  </button>
                ) : <span className="font-mono2 text-xs text-yellow-500">processing…</span>}
              </div>
            ))}
          </div>
        )}

        <div className="mt-4 inline-block border border-yellow-600/40 bg-yellow-950/20 px-4 py-2 font-mono2 text-xs text-yellow-500/90">
          {pending ? "Manual verification is temporary until the payment gateway is live" : "Card payment is mocked for now"}
        </div>
        {order?.telegram_deeplink && (
          <div className="mt-6">
            <a href={order.telegram_deeplink} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 border border-red-600/50 bg-red-600/10 px-6 py-3 text-sm font-semibold text-red-300 hover:bg-red-600/20 transition-colors clip-corner">
              <Send className="h-4 w-4" /> {pending ? "Track on Telegram" : "Receive key on Telegram"}
            </a>
            <p className="mt-2 font-mono2 text-[11px] text-zinc-600">Tap, then press START — {pending ? "you'll be notified here once verified." : "the bot sends your key instantly."}</p>
          </div>
        )}
        <div className="mt-8 flex justify-center gap-3">
          <button onClick={() => navigate("/account")} className="inline-flex items-center gap-2 bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner">
            View in account <ArrowRight className="h-4 w-4" />
          </button>
          <button onClick={() => navigate("/")} className="inline-flex items-center gap-2 border border-zinc-700 px-6 py-3 text-sm font-semibold text-white hover:border-red-600/60 transition-colors clip-corner">
            Back home
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
                { id: "upi", label: "UPI (QR)", sub: "GPay / PhonePe / Paytm", icon: Smartphone },
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

            {method === "upi" && (
              <div className="mt-5 border border-zinc-800 bg-zinc-950 p-5 clip-corner">
                <p className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Scan &amp; pay {currency === "inr" ? `₹${totalInr}` : `≈₹${totalInr}`}</p>
                <div className="mt-4 flex flex-col items-center gap-4 sm:flex-row sm:items-start">
                  {qrSrc ? (
                    <img src={qrSrc} alt="UPI QR" className="h-44 w-44 rounded-md border border-zinc-800 bg-white p-1" />
                  ) : (
                    <div className="flex h-44 w-44 flex-col items-center justify-center rounded-md border border-dashed border-zinc-700 text-center">
                      <Smartphone className="h-6 w-6 text-zinc-500" />
                      <p className="mt-2 px-3 font-mono2 text-[11px] text-zinc-500">Pay ₹{totalInr} to the UPI shown on Telegram — then paste the reference below.</p>
                    </div>
                  )}
                  <div className="flex-1">
                    <ol className="space-y-1.5 text-sm text-zinc-400">
                      <li>1. Scan the QR in any UPI app</li>
                      <li>2. Pay exactly <b className="text-white">₹{totalInr}</b></li>
                      <li>3. Paste the <b className="text-white">UPI reference / UTR</b> below</li>
                    </ol>
                    <label className="mt-3 block">
                      <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">UPI reference / UTR *</span>
                      <input value={paymentRef} onChange={(e) => setPaymentRef(e.target.value)} placeholder="e.g. 4536 1289 0071"
                        className="mt-1.5 w-full border border-zinc-800 bg-black px-3 py-2.5 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-red-600/60" />
                    </label>
                  </div>
                </div>
              </div>
            )}

            <button type="submit" disabled={busy} className="mt-7 inline-flex w-full items-center justify-center gap-2 bg-red-600 px-6 py-3.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors disabled:opacity-60 clip-corner">
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {method === "upi" ? `I've paid ${total} — submit` : `Pay ${total}`} <ArrowRight className="h-4 w-4" />
            </button>
            <p className="mt-3 flex items-center justify-center gap-1.5 font-mono2 text-[11px] text-zinc-600">
              <ShieldCheck className="h-3.5 w-3.5" /> {method === "upi" ? "Key is released after your payment is verified" : "Card payment is mocked in this preview"}
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
