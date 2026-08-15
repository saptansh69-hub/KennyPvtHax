import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { KeyRound, Loader2, LogOut, Package, User, Send, Copy, Check } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { useToast } from "../hooks/use-toast";

const Account = () => {
  const { user, loading, logout } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [copied, setCopied] = useState("");

  useEffect(() => {
    if (!loading && !user) navigate("/");
  }, [loading, user, navigate]);

  useEffect(() => {
    if (user) {
      api.get("/orders/me").then((res) => setOrders(res.data.orders)).finally(() => setLoadingOrders(false));
    }
  }, [user]);

  const copyKey = (key) => {
    navigator.clipboard?.writeText(key);
    setCopied(key);
    toast({ title: "Key copied", description: key });
    setTimeout(() => setCopied(""), 1500);
  };

  if (loading || !user) {
    return <div className="flex justify-center py-32"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>;
  }

  return (
    <div className="relative">
      <div className="radial-red absolute inset-x-0 top-0 h-60" />
      <div className="relative mx-auto max-w-5xl px-6 py-16">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div className="flex items-center gap-4">
            <span className="grid h-14 w-14 place-items-center border border-red-600/50 bg-red-600/10 clip-corner">
              <User className="h-7 w-7 text-red-500" />
            </span>
            <div>
              <h1 className="font-display text-2xl font-bold">{user.name}</h1>
              <p className="font-mono2 text-xs text-zinc-500">{user.email || user.telegram}</p>
            </div>
          </div>
          <button onClick={() => { logout(); navigate("/"); }}
            className="inline-flex items-center gap-2 border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-300 hover:border-red-600/60 hover:text-white transition-colors clip-corner">
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>

        <div className="mt-12 flex items-center gap-2">
          <Package className="h-5 w-5 text-red-500" />
          <h2 className="font-display text-xl font-bold">Your purchases</h2>
        </div>

        {loadingOrders ? (
          <div className="flex justify-center py-16"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>
        ) : orders.length === 0 ? (
          <div className="mt-6 border border-zinc-800 bg-zinc-900/40 p-10 text-center clip-corner">
            <KeyRound className="mx-auto h-8 w-8 text-zinc-600" />
            <p className="mt-3 text-sm text-zinc-500">No purchases yet.</p>
            <button onClick={() => navigate("/pricing")} className="mt-4 inline-flex items-center gap-2 bg-red-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors clip-corner">
              Buy your first key
            </button>
          </div>
        ) : (
          <div className="mt-6 space-y-5">
            {orders.map((o) => (
              <div key={o.id} className="border border-zinc-800 bg-zinc-900/40 p-6 clip-corner">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800 pb-4">
                  <div>
                    <p className="font-mono2 text-xs text-zinc-500">Order #{o.id.slice(0, 8).toUpperCase()}</p>
                    <p className="text-xs text-zinc-600">{new Date(o.created_at).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="border border-green-600/40 bg-green-600/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-green-400">
                      {o.status}
                    </span>
                    <span className="font-display font-bold text-red-500">
                      {o.currency === "inr" ? `₹${o.total_inr}` : `$${o.total_usd}`}
                    </span>
                  </div>
                </div>
                <div className="mt-4 space-y-3">
                  {o.keys?.map((k, i) => (
                    <div key={i} className="flex flex-wrap items-center justify-between gap-3 border border-zinc-800 bg-zinc-950 p-3">
                      <div>
                        <p className="text-sm font-semibold text-white">{k.project}</p>
                        <p className="font-mono2 text-xs text-zinc-500">{k.plan} · {k.duration}</p>
                      </div>
                      <button onClick={() => copyKey(k.key)}
                        className="inline-flex items-center gap-2 border border-red-900/50 bg-red-600/10 px-3 py-1.5 font-mono2 text-xs text-red-300 hover:bg-red-600/20 transition-colors">
                        {copied === k.key ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />} {k.key}
                      </button>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
                  <p className="flex items-center gap-1.5 font-mono2 text-[11px] text-zinc-600">
                    <Send className="h-3.5 w-3.5" /> {o.delivered ? `Delivered to ${o.telegram} on Telegram` : `For ${o.telegram}`}
                  </p>
                  {o.telegram_deeplink && (
                    <a href={o.telegram_deeplink} target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 border border-red-900/50 bg-red-600/10 px-3 py-1.5 font-mono2 text-[11px] text-red-300 hover:bg-red-600/20 transition-colors">
                      <Send className="h-3 w-3" /> Get on Telegram
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Account;
