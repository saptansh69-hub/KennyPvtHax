import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Package, Users, MessageSquare, KeyRound, IndianRupee, Send, Copy, Check, Trash2, ShieldAlert, Boxes, Plus } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { useToast } from "../hooks/use-toast";

const PROJECT_OPTS = [["", "Any project"], ["og", "OG Cheats"], ["frozen", "Frozen Fire"], ["admin", "Kenny Admin"]];
const PLAN_OPTS = [["", "Any plan"], ["1day", "1 Day"], ["7day", "7 Day"], ["month", "Month"], ["admin-week", "Admin Week"]];

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
  const [cfg, setCfg] = useState({ telegram_enabled: false, bot_username: null });
  const [summary, setSummary] = useState(null);
  const [loadingData, setLoadingData] = useState(true);
  const [copied, setCopied] = useState("");
  const [form, setForm] = useState({ projectId: "", planId: "", keys: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => { if (!loading && (!user || !user.is_admin)) navigate("/"); }, [loading, user, navigate]);

  const loadAll = async () => {
    try {
      const [s, o, f, c, k] = await Promise.all([
        api.get("/admin/stats"), api.get("/admin/orders"), api.get("/admin/feedback"),
        api.get("/config"), api.get("/admin/keys/summary"),
      ]);
      setStats(s.data); setOrders(o.data.orders); setFeedback(f.data.feedback); setCfg(c.data); setSummary(k.data);
    } catch { toast({ title: "Failed to load admin data" }); }
    finally { setLoadingData(false); }
  };
  useEffect(() => { if (user?.is_admin) loadAll(); }, [user]);

  const copy = (t) => { navigator.clipboard?.writeText(t); setCopied(t); setTimeout(() => setCopied(""), 1500); };
  const deleteFb = async (id) => { await api.delete(`/admin/feedback/${id}`); setFeedback((p) => p.filter((f) => f.id !== id)); toast({ title: "Review deleted" }); };

  const addKeys = async () => {
    const keys = form.keys.split(/\r?\n/).map((k) => k.trim()).filter(Boolean);
    if (!keys.length) { toast({ title: "Paste at least one key" }); return; }
    setBusy(true);
    try {
      const res = await api.post("/admin/keys/bulk", { projectId: form.projectId || null, planId: form.planId || null, keys });
      toast({ title: `Added ${res.data.added} key(s)`, description: res.data.skipped ? `${res.data.skipped} duplicates skipped` : "" });
      setForm((f) => ({ ...f, keys: "" }));
      loadAll();
    } catch (err) { toast({ title: "Failed", description: err?.response?.data?.detail || "Try again" }); }
    finally { setBusy(false); }
  };

  if (loading || !user?.is_admin) return <div className="flex justify-center py-32"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>;

  const money = (o) => (o.currency === "inr" ? `₹${o.total_inr}` : `$${o.total_usd}`);
  const tabs = [["orders", "Orders"], ["inventory", "Key Inventory"], ["feedback", "Reviews"]];
  const label = (v, opts) => (opts.find(([k]) => k === v) || [, v])[1];

  return (
    <div className="relative">
      <div className="radial-red absolute inset-x-0 top-0 h-52" />
      <div className="relative mx-auto max-w-6xl px-6 py-14">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center border border-red-600/50 bg-red-600/10 clip-corner"><ShieldAlert className="h-6 w-6 text-red-500" /></span>
          <div><h1 className="font-display text-2xl font-bold">Admin Panel</h1><p className="font-mono2 text-xs text-zinc-500">KennyPvtHax control center</p></div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3 font-mono2 text-xs">
          <span className={`inline-flex items-center gap-2 border px-3 py-1.5 ${cfg.telegram_enabled ? "border-green-600/40 bg-green-600/10 text-green-400" : "border-yellow-600/40 bg-yellow-950/20 text-yellow-500"}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${cfg.telegram_enabled ? "bg-green-400" : "bg-yellow-500"}`} /> Telegram {cfg.telegram_enabled ? `@${cfg.bot_username}` : "not configured"}
          </span>
          <span className="inline-flex items-center gap-2 border border-zinc-700 px-3 py-1.5 text-zinc-400">
            <Boxes className="h-3.5 w-3.5" /> {summary?.total_available ?? 0} keys in stock
          </span>
        </div>

        {loadingData ? (<div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>) : (
          <>
            <div className="mt-8 grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
              <Stat icon={Package} label="Orders" value={stats?.orders ?? 0} />
              <Stat icon={Boxes} label="Keys left" value={stats?.keys_available ?? 0} />
              <Stat icon={KeyRound} label="Keys sold" value={stats?.keys_used ?? 0} />
              <Stat icon={Users} label="Users" value={stats?.users ?? 0} />
              <Stat icon={IndianRupee} label="Revenue ₹" value={stats?.revenue_inr ?? 0} />
              <Stat icon={Send} label="Delivered" value={stats?.delivered ?? 0} />
            </div>

            <div className="mt-10 inline-flex flex-wrap border border-zinc-800 bg-zinc-900/60 p-1">
              {tabs.map(([id, lbl]) => (
                <button key={id} onClick={() => setTab(id)} className={`px-5 py-2 text-sm font-semibold font-mono2 transition-colors ${tab === id ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}>{lbl}</button>
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
                      <div className="flex items-center gap-2">
                        {!o.stock_ok && <span className="border border-yellow-600/40 bg-yellow-950/20 px-2 py-0.5 text-[10px] font-bold uppercase text-yellow-500">Out of stock</span>}
                        <span className={`border px-2 py-0.5 text-[10px] font-bold uppercase ${o.delivered ? "border-green-600/40 bg-green-600/10 text-green-400" : "border-zinc-700 text-zinc-400"}`}>{o.delivered ? "Delivered" : "Awaiting TG"}</span>
                        <span className="font-display font-bold text-red-500">{money(o)}</span>
                      </div>
                    </div>
                    <div className="mt-3 space-y-2">
                      {o.keys?.map((k, i) => (
                        <div key={i} className="flex flex-wrap items-center justify-between gap-2 border border-zinc-800 bg-zinc-950 p-2.5">
                          <span className="text-sm text-white">{k.project} · <span className="text-zinc-500">{k.plan}</span></span>
                          {k.key ? (
                            <button onClick={() => copy(k.key)} className="inline-flex items-center gap-2 border border-red-900/50 bg-red-600/10 px-3 py-1 font-mono2 text-xs text-red-300 hover:bg-red-600/20">
                              {copied === k.key ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />} {k.key}
                            </button>
                          ) : <span className="font-mono2 text-xs text-yellow-500">pending restock</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {tab === "inventory" && (
              <div className="mt-6 grid gap-6 lg:grid-cols-2">
                <div className="tech-card p-6 clip-corner">
                  <div className="flex items-center gap-2"><Plus className="h-5 w-5 text-red-500" /><h3 className="font-display text-lg font-bold">Add license keys</h3></div>
                  <p className="mt-1 text-xs text-zinc-500">Paste one key per line. Tag them to a project + plan so the right key is sent on purchase.</p>
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <label className="block"><span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Project</span>
                      <select value={form.projectId} onChange={(e) => setForm((f) => ({ ...f, projectId: e.target.value }))} className="mt-1 w-full border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-red-600/60">
                        {PROJECT_OPTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                      </select></label>
                    <label className="block"><span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Plan</span>
                      <select value={form.planId} onChange={(e) => setForm((f) => ({ ...f, planId: e.target.value }))} className="mt-1 w-full border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-red-600/60">
                        {PLAN_OPTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                      </select></label>
                  </div>
                  <textarea value={form.keys} onChange={(e) => setForm((f) => ({ ...f, keys: e.target.value }))} rows={8} placeholder={"KENNY-XXXX-XXXX\nKENNY-YYYY-YYYY"} className="mt-3 w-full resize-none border border-zinc-800 bg-zinc-950 px-3 py-2.5 font-mono2 text-sm text-white outline-none placeholder:text-zinc-700 focus:border-red-600/60" />
                  <button onClick={addKeys} disabled={busy} className="mt-3 inline-flex w-full items-center justify-center gap-2 bg-red-600 py-2.5 text-sm font-semibold text-white hover:bg-red-500 transition-colors disabled:opacity-50 clip-corner">
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />} Add to inventory
                  </button>
                </div>

                <div className="tech-card p-6 clip-corner">
                  <div className="flex items-center gap-2"><Boxes className="h-5 w-5 text-red-500" /><h3 className="font-display text-lg font-bold">Stock summary</h3></div>
                  <div className="mt-4 overflow-hidden border border-zinc-800">
                    <div className="grid grid-cols-4 bg-zinc-900 px-3 py-2 font-mono2 text-[11px] uppercase tracking-widest text-zinc-500">
                      <span className="col-span-2">Bucket</span><span>Left</span><span>Sold</span>
                    </div>
                    {(summary?.buckets || []).length === 0 && <p className="px-3 py-4 text-sm text-zinc-500">No keys added yet.</p>}
                    {(summary?.buckets || []).map((b, i) => (
                      <div key={i} className="grid grid-cols-4 border-t border-zinc-800 px-3 py-2.5 text-sm">
                        <span className="col-span-2 text-zinc-300">{label(b.projectId === "any" ? "" : b.projectId, PROJECT_OPTS)} · {label(b.planId === "any" ? "" : b.planId, PLAN_OPTS)}</span>
                        <span className="font-bold text-green-400">{b.available}</span>
                        <span className="text-zinc-500">{b.used}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {tab === "feedback" && (
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                {feedback.map((f) => (
                  <div key={f.id} className="tech-card p-5 clip-corner">
                    <div className="flex items-start justify-between">
                      <div><p className="font-display text-sm font-bold text-white">{f.name}</p><p className="font-mono2 text-[11px] text-red-400">Rating {f.rating}/5</p></div>
                      <button onClick={() => deleteFb(f.id)} className="text-zinc-500 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
                    </div>
                    <p className="mt-2 text-sm text-zinc-400">{f.message}</p>
                    {f.image && <img src={f.image} alt="" className="mt-3 h-28 w-full rounded object-cover border border-zinc-800" />}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Admin;
