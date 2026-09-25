"use client";

import { useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { supabase } from "@/lib/supabase";

const navigation = [
  { name: "Dashboard", path: "/dashboard", icon: "▦" },
  { name: "Upload Invoice", path: "/upload-invoice", icon: "↑" },
  { name: "Customer Profile", path: "/customer-profile", icon: "◉" },
  { name: "Prediction & Action", path: "/prediction-action", icon: "⌁" },
  { name: "Credit / Udhaar", path: "/credit-overview", icon: "₹" },
  { name: "Product Bundles", path: "/product-bundles", icon: "⌘" },
  { name: "Inventory Signals", path: "/inventory-signals", icon: "▤" },
];

export default function AppShell({
  children,
}: {
  children: ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  const [profileOpen, setProfileOpen] = useState(false);
  const [email, setEmail] = useState("");

  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadUser() {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (user?.email) {
        setEmail(user.email);
      }
    }

    loadUser();
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target as Node)
      ) {
        setProfileOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  if (pathname === "/") {
    return <>{children}</>;
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    setProfileOpen(false);
    router.push("/");
  }

  return (
    <div className="min-h-screen bg-[#f7f9fc]">

      {/* =========================
          DESKTOP SIDEBAR
      ========================== */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-gray-200 bg-white lg:flex lg:flex-col">

        <div className="flex h-20 items-center border-b border-gray-100 px-6">
          <button
            onClick={() => router.push("/dashboard")}
            className="flex items-center gap-3"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-lg font-bold text-white">
              R
            </div>

            <div className="text-left">
              <p className="text-lg font-bold tracking-tight text-gray-900">
                RetailMind
              </p>

              <p className="text-[11px] font-medium text-gray-400">
                AI for Retail
              </p>
            </div>
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
          <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-widest text-gray-400">
            Workspace
          </p>

          {navigation.map((item) => {
            const active = pathname === item.path;

            return (
              <button
                key={item.path}
                onClick={() => router.push(item.path)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition ${
                  active
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm ${
                    active
                      ? "bg-blue-100 text-blue-700"
                      : "bg-gray-50 text-gray-500"
                  }`}
                >
                  {item.icon}
                </span>

                {item.name}
              </button>
            );
          })}
        </nav>

        <div className="border-t border-gray-100 p-4">
          <div className="rounded-xl bg-gray-50 px-3 py-3">
            <p className="text-xs font-semibold text-gray-700">
              RetailMind AI
            </p>

            <p className="mt-1 text-[11px] text-gray-400">
              Business Intelligence
            </p>
          </div>
        </div>
      </aside>

      {/* =========================
          MOBILE TOP BAR
      ========================== */}
      <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 lg:hidden">

        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 font-bold text-white">
            R
          </div>

          <span className="font-bold text-gray-900">
            RetailMind
          </span>
        </button>

        <div ref={profileRef} className="relative">
          <button
            onClick={() => setProfileOpen((open) => !open)}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-[#111827] text-sm font-bold text-white"
          >
            VS
          </button>

          {profileOpen && (
            <ProfileMenu
              email={email}
              onLogout={handleLogout}
            />
          )}
        </div>
      </header>

      {/* =========================
          MAIN CONTENT
      ========================== */}
      <main className="min-h-screen lg:pl-64">
        {children}
      </main>

      {/* =========================
          FLOATING COPILOT
      ========================== */}
      <button
        onClick={() => router.push("/copilot")}
        aria-label="Open RetailMind AI Copilot"
        className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-full bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-xl shadow-blue-600/25 transition-all duration-200 hover:scale-105 hover:bg-blue-700 hover:shadow-2xl"
      >
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 text-lg">
          ✦
        </span>

        <span className="hidden sm:inline">
          Ask RetailMind AI
        </span>
      </button>

    </div>
  );
}

/* =========================
   PROFILE MENU
========================= */

function ProfileMenu({
  email,
  onLogout,
}: {
  email: string;
  onLogout: () => void;
}) {
  return (
    <div className="absolute right-0 top-12 z-50 w-72 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl">

      <div className="border-b border-gray-100 px-5 py-5">
        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#111827] text-sm font-bold text-white">
            VS
          </div>

          <div className="min-w-0">
            <p className="font-semibold text-gray-900">
              Retailer Account
            </p>

            <p className="mt-1 truncate text-xs text-gray-500">
              {email || "Logged-in account"}
            </p>
          </div>

        </div>
      </div>

      <div className="p-2">

        <div className="flex items-center gap-3 rounded-xl px-3 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-50 text-gray-500">
            👤
          </div>

          <div>
            <p className="text-sm font-medium text-gray-800">
              Account
            </p>

            <p className="text-xs text-gray-400">
              Your RetailMind account
            </p>
          </div>
        </div>

        <button
          onClick={onLogout}
          className="mt-1 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition hover:bg-red-50"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50 text-red-600">
            ↪
          </div>

          <div>
            <p className="text-sm font-medium text-red-600">
              Sign out
            </p>

            <p className="text-xs text-gray-400">
              End your current session
            </p>
          </div>
        </button>

      </div>
    </div>
  );
}