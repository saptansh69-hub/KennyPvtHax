import React, { createContext, useContext, useEffect, useState } from "react";

const CartContext = createContext(null);

const STORAGE_KEY = "kenny_cart";

export const CartProvider = ({ children }) => {
  const [items, setItems] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }, [items]);

  const addItem = (item) => {
    setItems((prev) => {
      const key = `${item.projectId}-${item.planId}`;
      if (prev.find((p) => `${p.projectId}-${p.planId}` === key)) return prev;
      return [...prev, { ...item, key }];
    });
  };

  const removeItem = (key) => setItems((prev) => prev.filter((p) => p.key !== key));
  const clearCart = () => setItems([]);

  const totalInr = items.reduce((s, i) => s + i.inr, 0);
  const totalUsd = items.reduce((s, i) => s + i.usd, 0);

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, clearCart, totalInr, totalUsd, count: items.length }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
};
