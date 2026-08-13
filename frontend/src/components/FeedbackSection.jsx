import React, { useEffect, useState } from "react";
import { Star, Loader2, Quote, Send } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../hooks/use-toast";

const Stars = ({ value, onChange, size = "h-4 w-4" }) => (
  <div className="flex items-center gap-0.5">
    {[1, 2, 3, 4, 5].map((n) => (
      <button
        key={n}
        type="button"
        disabled={!onChange}
        onClick={() => onChange?.(n)}
        className={onChange ? "transition-transform hover:scale-110" : "cursor-default"}
      >
        <Star className={`${size} ${n <= value ? "fill-red-500 text-red-500" : "text-zinc-600"}`} />
      </button>
    ))}
  </div>
);

const FeedbackSection = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: "", rating: 5, message: "" });
  const [busy, setBusy] = useState(false);

  const load = () => {
    api.get("/feedback").then((res) => setItems(res.data.feedback)).finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (user?.name) setForm((f) => ({ ...f, name: user.name }));
  }, [user]);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.message.trim()) return;
    setBusy(true);
    try {
      await api.post("/feedback", { name: form.name || "Anonymous", rating: form.rating, message: form.message });
      toast({ title: "Thanks for the feedback", description: "Your review is now live." });
      setForm((f) => ({ ...f, message: "" }));
      load();
    } catch {
      toast({ title: "Could not submit", description: "Please try again." });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section id="feedback" className="relative border-t border-zinc-800/80 py-20 md:py-28">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center">
          <p className="font-mono2 text-xs uppercase tracking-widest text-red-500">Community / feedback</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight md:text-5xl">
            What the <span className="text-red-500">squad</span> says
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-sm text-zinc-500">
            Real reviews from players running KennyPvtHax across PUBGM &amp; BGMI.
          </p>
        </div>

        <div className="mt-14 grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            {loading ? (
              <div className="flex justify-center py-16"><Loader2 className="h-6 w-6 animate-spin text-red-500" /></div>
            ) : (
              <div className="grid gap-5 sm:grid-cols-2">
                {items.map((f) => (
                  <div key={f.id} className="relative border border-zinc-800 bg-zinc-900/40 p-6 clip-corner">
                    <Quote className="h-6 w-6 text-red-600/60" />
                    <p className="mt-3 text-sm leading-relaxed text-zinc-300">{f.message}</p>
                    <div className="mt-5 flex items-center justify-between">
                      <div>
                        <p className="font-display text-sm font-bold text-white">{f.name}</p>
                        <Stars value={f.rating} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit form */}
          <form onSubmit={submit} className="h-fit border border-red-900/40 bg-zinc-900/40 p-6 clip-corner">
            <h3 className="font-display text-lg font-bold">Leave a review</h3>
            <p className="mt-1 text-xs text-zinc-500">Share your experience with the community.</p>
            <div className="mt-4 space-y-4">
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Your name / gamertag"
                className="w-full border border-zinc-800 bg-zinc-950 px-3 py-2.5 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-red-600/60"
              />
              <div className="flex items-center justify-between">
                <span className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">Rating</span>
                <Stars value={form.rating} onChange={(n) => setForm((f) => ({ ...f, rating: n }))} size="h-5 w-5" />
              </div>
              <textarea
                value={form.message}
                onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
                required
                rows={4}
                placeholder="Tell us how it went..."
                className="w-full resize-none border border-zinc-800 bg-zinc-950 px-3 py-2.5 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-red-600/60"
              />
              <button type="submit" disabled={busy}
                className="inline-flex w-full items-center justify-center gap-2 bg-red-600 py-3 text-sm font-semibold text-white hover:bg-red-500 transition-colors disabled:opacity-60 clip-corner">
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />} Post review
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
};

export default FeedbackSection;
