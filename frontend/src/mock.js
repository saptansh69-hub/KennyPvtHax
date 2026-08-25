// Site content. Catalog is intentionally empty — fill in the new product data here.
// Every export below is consumed by components, so keep the shapes even when empty.

// --- Branding ---
// siteNameAccent renders in the accent colour immediately after siteName.
export const siteName = "New Project";
export const siteNameAccent = "";
export const siteTagline = "";
export const siteDescription = "";

export const serverStatus = {
  status: "ONLINE",
  statusLabel: "All systems operational",
  lastUpdate: null,
  version: "",
  activeUsers: 0,
};

export const navLinks = [
  { label: "Home", to: "/" },
  { label: "Products", to: "/#projects" },
  { label: "Features", to: "/features" },
  { label: "Pricing", to: "/pricing" },
  { label: "Reviews", to: "/#feedback" },
];

// Each entry: { id, code, name, tagline, description, image, demoVideo, features[], accent, hasAdmin }
export const projects = [];

// Plan tiers keyed by group. Each plan: { id, label, duration, inr, usd, popular }
export const pricingPlans = {
  standard: [],
  admin: [],
};

// Buildable product list = each project x its available plans
export const products = [];

// Each entry: { code, title, desc }
export const coreFeatures = [];

// Each entry: { value, label }
export const showcaseStats = [];

// Each entry: { q, a }
export const faqs = [];

// --- Contact ---
export const telegramHandle = "";
export const telegramUrl = "";
export const ownerHandle = "";
export const ownerUrl = "";
export const logoSrc = "";

// --- Media ---
export const heroBgVideo = "";
export const featuredShowcaseVideo = "";

// Promo/sale. Inactive while startISO === endISO.
export const promo = {
  label: "",
  startISO: "1970-01-01T00:00:00Z",
  endISO: "1970-01-01T00:00:00Z",
  discountedProjects: [],
  discountInr: {},
  discountUsd: {},
  qrByAmount: {},
};
