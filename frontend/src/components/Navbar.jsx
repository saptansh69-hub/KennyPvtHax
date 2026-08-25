import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Menu, X, ShoppingCart, User, LogIn, ShieldAlert } from "lucide-react";
import { navLinks, logoSrc, siteName, siteNameAccent } from "../mock";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui/button";
import AuthModal from "./AuthModal";

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const { count } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const handleNav = (to) => {
    setOpen(false);
    if (to.startsWith("/#")) {
      const id = to.slice(2);
      if (location.pathname !== "/") {
        navigate("/");
        setTimeout(() => document.getElementById(id)?.scrollIntoView({ behavior: "smooth" }), 250);
      } else {
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
      }
    } else {
      navigate(to);
    }
  };

  return (
    <header className={`sticky top-0 z-50 w-full transition-all duration-300 ${scrolled ? "border-b border-zinc-800/80 glass" : "border-b border-transparent bg-transparent"}`}>
      <nav className="mx-auto max-w-7xl px-6">
        <div className="flex h-16 items-center justify-between">
          <button onClick={() => handleNav("/")} className="flex items-center gap-2.5 group">
            {logoSrc && <img src={logoSrc} alt={siteName} className="h-9 w-9 rounded-md border border-red-600/50 object-cover" />}
            <span className="font-display text-lg font-bold tracking-tight">
              {siteName}<span className="text-red-500">{siteNameAccent}</span>
            </span>
          </button>

          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((l) => (
              <button key={l.label} onClick={() => handleNav(l.to)}
                className="px-4 py-2 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
                {l.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <button onClick={() => navigate("/checkout")} className="relative p-2 text-zinc-300 hover:text-white transition-colors">
              <ShoppingCart className="h-5 w-5" />
              {count > 0 && (
                <span className="absolute -right-1 -top-1 grid h-4 w-4 place-items-center rounded-full bg-red-600 text-[10px] font-bold text-white">{count}</span>
              )}
            </button>

            {user ? (
              <>
                {user.is_admin && (
                  <button onClick={() => navigate("/admin")}
                    className="hidden sm:inline-flex items-center gap-2 border border-red-600/50 bg-red-600/10 px-3 py-2 text-sm font-semibold text-red-300 hover:bg-red-600/20 transition-colors clip-corner">
                    <ShieldAlert className="h-4 w-4" /> Admin
                  </button>
                )}
                <button onClick={() => navigate("/account")}
                  className="inline-flex items-center gap-2 border border-zinc-700 px-3 py-2 text-sm font-semibold text-zinc-200 hover:border-red-600/60 transition-colors clip-corner">
                  <User className="h-4 w-4 text-red-500" />
                  <span className="hidden sm:inline max-w-[90px] truncate">{user.name}</span>
                </button>
              </>
            ) : (
              <button onClick={() => setAuthOpen(true)}
                className="hidden sm:inline-flex items-center gap-2 text-sm font-semibold text-zinc-300 hover:text-white transition-colors px-2">
                <LogIn className="h-4 w-4" /> Sign in
              </button>
            )}

            <Button onClick={() => navigate("/pricing")} className="hidden sm:inline-flex bg-red-600 hover:bg-red-500 text-white font-semibold clip-corner">
              Buy Key
            </Button>
            <button className="md:hidden p-2 text-zinc-300" onClick={() => setOpen((v) => !v)}>
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </nav>

      {open && (
        <div className="md:hidden border-t border-zinc-800 glass">
          <div className="px-6 py-3 space-y-1">
            {navLinks.map((l) => (
              <button key={l.label} onClick={() => handleNav(l.to)}
                className="block w-full text-left px-3 py-2.5 text-sm font-medium text-zinc-300 hover:text-white hover:bg-zinc-800/60 rounded">
                {l.label}
              </button>
            ))}
            {!user && (
              <button onClick={() => { setOpen(false); setAuthOpen(true); }}
                className="block w-full text-left px-3 py-2.5 text-sm font-semibold text-red-400">
                Sign in / Join
              </button>
            )}
          </div>
        </div>
      )}

      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} onSuccess={() => navigate("/account")} />
    </header>
  );
};

export default Navbar;
