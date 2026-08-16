import { promo } from "../mock";

export const promoActive = (now = Date.now()) => {
  const s = new Date(promo.startISO).getTime();
  const e = new Date(promo.endISO).getTime();
  return now >= s && now < e;
};

export const promoEndMs = () => new Date(promo.endISO).getTime();

// Effective INR/USD price for a project+plan (applies sale when active)
export const effectivePrice = (projectId, planId, baseInr, baseUsd) => {
  if (
    promoActive() &&
    promo.discountedProjects.includes(projectId) &&
    promo.discountInr[planId] != null
  ) {
    return { inr: promo.discountInr[planId], usd: promo.discountUsd[planId] ?? baseUsd, sale: true };
  }
  return { inr: baseInr, usd: baseUsd, sale: false };
};

export const qrForAmount = (inr) => promo.qrByAmount[inr] || null;

// Returns {d,h,m,s,total} remaining until promo end
export const timeLeft = (now = Date.now()) => {
  let ms = Math.max(0, promoEndMs() - now);
  const total = ms;
  const d = Math.floor(ms / 86400000); ms -= d * 86400000;
  const h = Math.floor(ms / 3600000); ms -= h * 3600000;
  const m = Math.floor(ms / 60000); ms -= m * 60000;
  const s = Math.floor(ms / 1000);
  return { d, h, m, s, total };
};

export const pad = (n) => String(n).padStart(2, "0");
