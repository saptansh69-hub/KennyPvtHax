// Mock data for KennyPvtHax — frontend-only teaser (to be replaced by backend)

export const serverStatus = {
  status: "ONLINE",
  statusLabel: "All systems operational",
  lastPatch: "2025-07-14T09:32:00Z",
  version: "v4.7.2",
  undetected: true,
  activeUsers: 2847,
};

export const navLinks = [
  { label: "Home", to: "/" },
  { label: "Projects", to: "/#projects" },
  { label: "Features", to: "/features" },
  { label: "Pricing", to: "/pricing" },
  { label: "Download", to: "/download" },
];

export const projects = [
  {
    id: "og",
    code: "01",
    name: "OG Cheats",
    tagline: "The market standard",
    description:
      "Featuring the market's most common UI. Clean, reliable and battle-tested — everything a player expects with rock-solid stability.",
    image:
      "https://images.unsplash.com/photo-1590845947376-2638caa89309?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxtb2JpbGUlMjBnYW1pbmd8ZW58MHx8fHJlZHwxNzg2NjU2OTk1fDA&ixlib=rb-4.1.0&q=85",
    features: ["Aimbot & ESP", "Standard menu UI", "Stable runtime", "Anti-ban base"],
    accent: "#ff3b3b",
    hasAdmin: false,
  },
  {
    id: "frozen",
    code: "02",
    name: "Frozen Fire",
    tagline: "Advanced & stream-safe",
    description:
      "An advanced version of the UI with the ability to hide ESP while recording. Built for creators who need to stay invisible on stream.",
    image:
      "https://images.unsplash.com/photo-1650765814764-aeae1a900dfa?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMjh8MHwxfHNlYXJjaHwxfHxkYXJrJTIwZXNwb3J0c3xlbnwwfHx8cmVkfDE3ODY2NTY5OTV8MA&ixlib=rb-4.1.0&q=85",
    features: ["Hide ESP while recording", "Advanced UI", "Stream mode", "Priority updates"],
    accent: "#ff5a1f",
    hasAdmin: false,
  },
  {
    id: "admin",
    code: "03",
    name: "Kenny Admin",
    tagline: "True potential — demo only",
    description:
      "The best of all. A display of true potential and power, only for those who want to prove they are the best. Gives all imaginary powers to beat other hackers — strictly for demonstration and fun purposes.",
    image:
      "https://images.unsplash.com/photo-1558008258-7ff8888b42b0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzV8MHwxfHNlYXJjaHwzfHxlc3BvcnRzfGVufDB8fHxibGFja3wxNzg2NjU3MDAxfDA&ixlib=rb-4.1.0&q=85",
    features: ["God-tier control", "Anti-hacker override", "Demonstration mode", "Exclusive access"],
    accent: "#e50914",
    hasAdmin: true,
  },
];

// Pricing plans. OG & Frozen share the same standard tiers. Admin is weekly-only.
export const pricingPlans = {
  standard: [
    { id: "1day", label: "1 Day", duration: "24 hours", inr: 120, usd: 1, popular: false },
    { id: "7day", label: "7 Day", duration: "1 week", inr: 600, usd: 6, popular: true },
    { id: "month", label: "Month Access", duration: "30 days", inr: 1500, usd: 15, popular: false },
  ],
  admin: [
    { id: "admin-week", label: "Admin Key", duration: "1 week subscription", inr: 1000, usd: 10, popular: true },
  ],
};

// Buildable product list = each project x its available plans
export const products = [
  { project: "OG Cheats", projectId: "og", plans: pricingPlans.standard },
  { project: "Frozen Fire", projectId: "frozen", plans: pricingPlans.standard },
  { project: "Kenny Admin", projectId: "admin", plans: pricingPlans.admin },
];

export const coreFeatures = [
  { code: "01", title: "Kernel-level support", desc: "External kernel architecture for a stable, low-footprint runtime." },
  { code: "02", title: "Anti-cheat bypass", desc: "Continuously updated evasion layer that stays ahead of detection." },
  { code: "03", title: "Real-time protection", desc: "Live guard that pauses risky actions automatically." },
  { code: "04", title: "Around-the-clock support", desc: "24/7 Telegram support for keys, setup and troubleshooting." },
  { code: "05", title: "Custom features", desc: "Configurable aimbot, ESP and visuals tuned to your playstyle." },
  { code: "06", title: "Stream mode", desc: "Hide overlays while recording so your gameplay stays clean." },
];

export const showcaseStats = [
  { value: "2.8K+", label: "Active users" },
  { value: "99.9%", label: "Uptime" },
  { value: "< 2h", label: "Patch turnaround" },
  { value: "24/7", label: "Telegram support" },
];

export const faqs = [
  { q: "How do I receive my key after payment?", a: "Your key is generated instantly after checkout and delivered to the Telegram username you provide at checkout." },
  { q: "Which games are supported?", a: "KennyPvtHax supports PUBG Mobile (Global) and BGMI (India) across current versions." },
  { q: "Is Kenny Admin real?", a: "Kenny Admin is a demonstration build made for fun. Its 'imaginary powers' are for showcasing capability only." },
  { q: "What payment methods do you accept?", a: "We accept UPI (India) and Stripe card payments (international). More options coming soon." },
];

export const telegramHandle = "@KennyPvtHax";
export const telegramUrl = "https://t.me/KennyPvtHax";
