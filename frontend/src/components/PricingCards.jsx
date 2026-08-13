import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check, ShoppingCart, Crown, Zap } from "lucide-react";
import { products } from "../mock";
import { useCart } from "../context/CartContext";
import { useToast } from "../hooks/use-toast";

const currencies = [
  { id: "inr", label: "INR ₹" },
  { id: "usd", label: "USD $" },
];

const PricingCards = () => {
  const [currency, setCurrency] = useState("inr");
  const { addItem } = useCart();
  const { toast } = useToast();
  const navigate = useNavigate();

  const price = (plan) => (currency === "inr" ? `₹${plan.inr}` : `$${plan.usd}`);

  const handleAdd = (product, plan) => {
    addItem({
      projectId: product.projectId,
      project: product.project,
      planId: plan.id,
      plan: plan.label,
      duration: plan.duration,
      inr: plan.inr,
      usd: plan.usd,
    });
    toast({
      title: "Added to cart",
      description: `${product.project} · ${plan.label} (${plan.duration})`,
    });
  };

  return (
    <div>
      <div className="mb-10 flex justify-center">
        <div className="inline-flex border border-zinc-800 bg-zinc-900/60 p-1">
          {currencies.map((c) => (
            <button
              key={c.id}
              onClick={() => setCurrency(c.id)}
              className={`px-5 py-2 text-sm font-semibold font-mono2 transition-colors ${
                currency === c.id ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-12">
        {products.map((product) => {
          const isAdmin = product.projectId === "admin";
          return (
            <div key={product.projectId}>
              <div className="mb-5 flex items-center gap-3">
                {isAdmin ? <Crown className="h-5 w-5 text-red-500" /> : <Zap className="h-5 w-5 text-red-500" />}
                <h3 className="font-display text-xl font-bold md:text-2xl">{product.project}</h3>
                {isAdmin && (
                  <span className="border border-red-600/60 bg-red-600/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-red-300">
                    Subscription only
                  </span>
                )}
              </div>

              <div className={`grid gap-5 ${isAdmin ? "md:grid-cols-1 lg:max-w-md" : "md:grid-cols-3"}`}>
                {product.plans.map((plan) => (
                  <div
                    key={plan.id}
                    className={`relative flex flex-col border p-6 transition-all duration-300 clip-corner ${
                      plan.popular
                        ? "border-red-600/70 bg-red-600/5"
                        : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700"
                    }`}
                  >
                    {plan.popular && (
                      <span className="absolute right-4 top-4 border border-red-600/60 bg-red-600/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-red-300">
                        Popular
                      </span>
                    )}
                    <p className="font-mono2 text-xs uppercase tracking-widest text-zinc-500">{plan.duration}</p>
                    <h4 className="mt-1 font-display text-lg font-bold">{plan.label}</h4>
                    <div className="mt-4 flex items-end gap-1">
                      <span className="font-display text-4xl font-bold text-white">{price(plan)}</span>
                      <span className="mb-1 text-sm text-zinc-500">/ {plan.duration}</span>
                    </div>
                    <ul className="mt-5 space-y-2 text-sm text-zinc-400">
                      <li className="flex items-center gap-2"><Check className="h-4 w-4 text-red-500" /> Instant Telegram key</li>
                      <li className="flex items-center gap-2"><Check className="h-4 w-4 text-red-500" /> Full feature access</li>
                      <li className="flex items-center gap-2"><Check className="h-4 w-4 text-red-500" /> Free updates during key</li>
                      {isAdmin && <li className="flex items-center gap-2"><Check className="h-4 w-4 text-red-500" /> All imaginary powers (demo)</li>}
                    </ul>
                    <button
                      onClick={() => handleAdd(product, plan)}
                      className={`mt-6 inline-flex items-center justify-center gap-2 px-4 py-3 text-sm font-semibold transition-colors clip-corner ${
                        plan.popular
                          ? "bg-red-600 text-white hover:bg-red-500"
                          : "border border-zinc-700 bg-zinc-800/60 text-white hover:border-red-600/60 hover:bg-red-600/10"
                      }`}
                    >
                      <ShoppingCart className="h-4 w-4" /> Add to cart
                    </button>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-12 flex justify-center">
        <button
          onClick={() => navigate("/checkout")}
          className="inline-flex items-center gap-2 border border-red-600/50 bg-red-600/10 px-6 py-3 text-sm font-semibold text-red-300 hover:bg-red-600/20 transition-colors clip-corner"
        >
          <ShoppingCart className="h-4 w-4" /> Go to checkout
        </button>
      </div>
    </div>
  );
};

export default PricingCards;
