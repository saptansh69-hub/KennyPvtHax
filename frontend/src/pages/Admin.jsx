import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Package, Users, MessageSquare, KeyRound, IndianRupee, Send, Copy, Check, Trash2, ShieldAlert, Zap } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { useToast } from "../hooks/use-toast";

const Stat = ({ icon: Icon, label, value }) => (
  <div className="tech-card p-5 clip-corner">
    <Icon className="h-5 w-5 text-red-500" />
    <p className="mt-3 font-display text-2xl font-bold text-white">{value}</p>
    <p className="font-mono2 text-[11px] uppercase tracking-widest text-zinc-500">{label}</p>
  </div>
);

const Admin = () => {
  const { user, loading } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [tab, setTab] = useState("orders");
  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [cfg, setCfg] = useState({ keyauth_enabled: false, telegram_enabled: false });
  const [loadingData, setLoadingData] = useState(true);
  const [copied, setCopied] = useState("");
  const [gen, setGen] = useState({ expiry_days: 7, amount: 1, note: "manual" });
  const [genKeys, setGenKeys] = useState([]);
  const [genBusy, setGenBusy] = useState(false);

  useEffect(() => {
    if (!loading && (!user || !user.is_admin)) navigate("/");
  }, [loading, user, navigate]);

  const loadAll = async () => {
    try {
      const [s, o, f, c] = await Promise.all([
        api.get("/admin/stats"), api.get("/admin/orders"),
        api.get("/admin/feedback"), api.get("/config"),
      ]);
      setStats(s.data); setOrders(o.data.orders); setFeedback(f.data.feedback); setCfg(c.data);
    } catch {
      toast({ title: "Failed to load admin data" });
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => { if (user?.is_admin) loadAll(); }, [user]);

  const copy = (t) => { navigator.clipboard?.writeText(t); setCopied(t); setTimeout(() => setCopied(""), 1500); };

  const deleteFb = async (id) => {
    await api.delete(`/admin/feedback/${id}`);
    setFeedback((prev) => prev.filter((f) => f.id !== id));
    toast({ title: "Review deleted" });
  };

  const generate = async () => {
    setGenBusy(true);
    try {
      const res = await api.post("/admin/keyauth/generate", gen);
      setGenKeys(res.data.keys);
      toast({ title: `Generated ${res.data.keys.length} key(s)` });
    } catch (err) {
      toast({ title: "Generate failed", description: err?.response?.data?.detail || "Check KeyAuth config" });
    } finally {
      setGenBusy(false);
    }
  };

  if (loading || !user?.is_admin) {
    return <div className="flex justify-center py-32"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>;
  }

  const money = (o) => (o.currency === "inr" ? `₹${o.total_inr}` : `$${o.total_usd}`);
  const tabs = [["orders", "Orders"], ["feedback", "Reviews"], ["keyauth", "KeyAuth"]];

  return (
    <div className="relative">
      <div className="radial-red absolute inset-x-0 top-0 h-52" />
      <div className="relative mx-auto max-w-6xl px-6 py-14">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center border border-red-600/50 bg-red-600/10 clip-corner">
            <ShieldAlert className="h-6 w-6 text-red-500" />
          </span>
          <div>
            <h1 className="font-display text-2xl font-bold">Admin Panel</h1>
            <p className="font-mono2 text-xs text-zinc-500">KennyPvtHax control center</p>
          </div>
        </div>

        {/* config chips */}
        <div className="mt-5 flex flex-wrap gap-3 font-mono2 text-xs">
          <span className={`inline-flex items-center gap-2 border px-3 py-1.5 ${cfg.keyauth_enabled ? "border-green-600/40 bg-green-600/10 text-green-400" : "border-yellow-600/40 bg-yellow-950/20 text-yellow-500"}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${cfg.keyauth_enabled ? "bg-green-400" : "bg-yellow-500"}`} /> KeyAuth {cfg.keyauth_enabled ? "connected" : "not configured"}
          </span>
          <span className={`inline-flex items-center gap-2 border px-3 py-1.5 ${cfg.telegram_enabled ? "border-green-600/40 bg-green-600/10 text-green-400" : "border-yellow-600/40 bg-yellow-950/20 text-yellow-500"}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${cfg.telegram_enabled ? "bg-green-400" : "bg-yellow-500"}`} /> Telegram bot {cfg.telegram_enabled ? "connected" : "not configured"}
          </span>
        </div>

        {loadingData ? (
          <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>
        ) : (
          <>
            <div className="mt-8 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
              <Stat icon={Package} label="Orders" value={stats?.orders ?? 0} />
              <Stat icon={KeyRound} label="Keys" value={stats?.keys_generated ?? 0} />
              <Stat icon={Users} label="Users" value={stats?.users ?? 0} />
              <Stat icon={MessageSquare} label="Reviews" value={stats?.feedback ?? 0} />
              <Stat icon={IndianRupee} label="Revenue ₹" value={stats?.revenue_inr ?? 0} />
              <Stat icon={Send} label="Delivered" value={stats?.delivered ?? 0} />
            </div>

            <div className="mt-10 inline-flex border border-zinc-800 bg-zinc-900/60 p-1">
              {tabs.map(([id, lbl]) => (
                <button key={id} onClick={() => setTab(id)}
                  className={`px-5 py-2 text-sm font-semibold font-mono2 transition-colors ${tab === id ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}>
                  {lbl}
                </button>
              ))}
            </div>

            {tab === "orders" && (
              <div className="mt-6 space-y-4">
                {orders.length === 0 && <p className="text-sm text-zinc-500">No orders yet.</p>}
                {orders.map((o) => (
                  <div key={o.id} className="tech-card p-5 clip-corner">
                    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800 pb-3">
                      <div>
                        <p className="font-mono2 text-xs text-zinc-400">#{o.id.slice(0, 8).toUpperCase()} · {o.telegram}</p>
                        <p className="text-xs text-zinc-600">{new Date(o.created_at).toLocaleString()} · {o.method?.toUpperCase()}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`border px-2 py-0.5 text-[10px] font-bold uppercase ${o.delivered ? "border-green-600/40 bg-green-600/10 text-green-400" : "border-zinc-700 text-zinc-400"}`}>
                          {o.delivered ? "Delivered" : "Not sent"}
                        </span>
                        <span className="font-display font-bold text-red-500">{money(o)}</span>
                      </div>
                    </div>
                    <div className="mt-3 space-y-2">
                      {o.keys?.map((k, i) => (
                        <div key={i} className="flex flex-wrap items-center justify-between gap-2 border border-zinc-800 bg-zinc-950 p-2.5">
                          <span className="text-sm text-white">{k.project} · <span className="text-zinc-500">{k.plan}</span>
                            <span className="ml-2 font-mono2 text-[10px] uppercase text-zinc-600">{k.source}</span></span>
                          <button onClick={() => copy(k.key)} className="inline-flex items-center gap-2 border border-red-900/50 bg-red-600/10 px-3 py-1 font-mono2 text-xs text-red-300 hover:bg-red-600/20">
                            {copied === k.key ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />} {k.key}
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {tab === "feedback" && (
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                {feedback.map((f) => (
                  <div key={f.id} className="tech-card p-5 clip-corner">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-display text-sm font-bold text-white">{f.name}</p>
                        <p className="font-mono2 text-[11px] text-red-400">Rating {f.rating}/5</p>
                      </div>
                      <button onClick={() => deleteFb(f.id)} className="text-zinc-500 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
                    </div>
                    <p className="mt-2 text-sm text-zinc-400">{f.message}</p>
                    {f.image && <img src={f.image} alt="" className="mt-3 h-28 w-full rounded object-cover border border-zinc-800" />}
                  </div>
                ))}
              </div>
            )}

            {tab === "keyauth" && (
              <div className="mt-6 max-w-lg">
                <div className="tech-card p-6 clip-corner">
                  <div className="flex items-center gap-2"><Zap className="h-5 w-5 text-red-500" /><h3 className="font-display text-lg font-bold">Generate keys via KeyAuth</h3></div>
                  {!cfg.keyauth_enabled && (
                    <p className="mt-3 border border-yellow-600/40 bg-yellow-950/20 p-3 font-mono2 text-xs text-yellow-500">
                      KeyAuth seller key not configured yet. Add it to activate live generation.
                    </p>
                  )}
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <label className="block">
                      <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Expiry (days)</span>
                      <input type="number" min={1} value={gen.expiry_days} onChange={(e) => setGen((g) => ({ ...g, expiry_days: +e.target.value }))}
                        className="mt-1 w-full border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-red-600/60" />
                    </label>
                    <label className="block">
                      <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Amount</span>
                      <input type="number" min={1} max={20} value={gen.amount} onChange={(e) => setGen((g) => ({ ...g, amount: +e.target.value }))}
                        className="mt-1 w-full border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-red-600/60" />
                    </label>
                  </div>
                  <button onClick={generate} disabled={genBusy || !cfg.keyauth_enabled}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 bg-red-600 py-2.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors disabled:opacity-50 clip-corner">
                    {genBusy ? <Loader2 className="h-4 w-4 animate-spin" /> : <KeyRound className="h-4 w-4" />} Generate
                  </button>
                  {genKeys.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {genKeys.map((k) => (
                        <button key={k} onClick={() => copy(k)} className="flex w-full items-center justify-between border border-zinc-800 bg-zinc-950 px-3 py-2 font-mono2 text-xs text-red-300 hover:bg-red-600/10">
                          {k} {copied === k ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Admin;
