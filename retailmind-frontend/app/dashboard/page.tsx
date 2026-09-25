"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type Product = {
  product_name: string;
  total_revenue: number;
};

type DashboardData = {
  summary: {
    total_revenue: number;
    total_orders: number;
    total_customers: number;
    average_order_value: number;
  };
  hero_products: Product[];
  weak_products: Product[];
};

export default function Dashboard() {
  const router = useRouter();

  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [profileOpen, setProfileOpen] = useState(false);
  const [email, setEmail] = useState("");

  const profileRef = useRef<HTMLDivElement>(null);

  async function loadDashboard() {
    try {
      setError("");

      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session?.access_token) {
        router.push("/");
        return;
      }

      const response = await fetch(`${API_URL}/dashboard`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Could not load dashboard data.");
      }

      const result = await response.json();

      console.log("DASHBOARD API RESPONSE:", result);
      setData(result);
    } catch (err) {
      console.error(err);
      setError("Could not load dashboard data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

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

  async function handleLogout() {
    await supabase.auth.signOut();
    setProfileOpen(false);
    router.push("/");
  }

  function handleRefresh() {
    setRefreshing(true);
    loadDashboard();
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />

          <p className="mt-4 text-sm text-gray-500">
            Loading your business data...
          </p>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center px-6">
        <div className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">

          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
            !
          </div>

          <h1 className="mt-4 text-lg font-semibold text-gray-900">
            Something went wrong
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            {error || "Could not load dashboard data."}
          </p>

          <button
            onClick={handleRefresh}
            className="mt-6 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Try Again
          </button>

        </div>
      </main>
    );
  }

  const { summary, hero_products, weak_products } = data;

  return (
    <main className="min-h-screen bg-[#f7f9fc] text-gray-900">

      {/* =========================
          TOP NAVIGATION
      ========================== */}
      <header className="border-b border-gray-200 bg-white">

        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

          {/* Logo */}
          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 font-bold text-white">
              R
            </div>

            <div>
              <h1 className="text-base font-bold">
                RetailMind AI
              </h1>

              <p className="text-[10px] font-medium uppercase tracking-wider text-gray-400">
                Business Intelligence
              </p>
            </div>

          </div>

          {/* Right Side */}
          <div className="flex items-center gap-4">

            {/* Refresh */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:opacity-50"
            >
              {refreshing ? "Refreshing..." : "Refresh"}
            </button>

            {/* Profile */}
            <div
              ref={profileRef}
              className="relative"
            >

              <button
                onClick={() => setProfileOpen((open) => !open)}
                aria-label="Open profile menu"
                aria-expanded={profileOpen}
                className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-900 text-xs font-bold text-white transition hover:bg-gray-800 hover:ring-4 hover:ring-gray-100"
              >
                VS
              </button>

              {/* Profile Dropdown */}
              {profileOpen && (
                <div className="absolute right-0 top-12 z-[100] w-72 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl">

                  {/* Account Header */}
                  <div className="border-b border-gray-100 px-5 py-5">

                    <div className="flex items-center gap-3">

                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-gray-900 text-sm font-bold text-white">
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

                  {/* Account Info */}
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

                    {/* Sign Out */}
                    <button
                      onClick={handleLogout}
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
              )}

            </div>

          </div>

        </div>

      </header>

      {/* =========================
          MAIN CONTENT
      ========================== */}
      <div className="mx-auto max-w-7xl px-6 py-8">

        {/* Heading */}
        <div className="mb-8">

          <p className="text-sm font-medium text-blue-600">
            Business Overview
          </p>

          <h2 className="mt-1 text-3xl font-bold tracking-tight">
            Dashboard
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Monitor your store performance and product activity.
          </p>

        </div>

        {/* Overview Cards */}
        <section className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

          <StatCard
            title="Total Revenue"
            value={`₹${Number(summary.total_revenue).toLocaleString("en-IN")}`}
          />

          <StatCard
            title="Total Orders"
            value={summary.total_orders.toLocaleString("en-IN")}
          />

          <StatCard
            title="Total Customers"
            value={summary.total_customers.toLocaleString("en-IN")}
          />

          <StatCard
            title="Average Order Value"
            value={`₹${Number(summary.average_order_value).toLocaleString(
              "en-IN",
              {
                maximumFractionDigits: 2,
              }
            )}`}
          />

        </section>

        {/* Products */}
        <section className="mt-8 grid gap-6 lg:grid-cols-2">

          <ProductCard
            title="Hero Products"
            subtitle="Products generating the most revenue"
            icon="↑"
            products={hero_products}
            positive
          />

          <ProductCard
            title="Weak Products"
            subtitle="Products with lower revenue contribution"
            icon="↓"
            products={weak_products}
          />

        </section>

      </div>

    </main>
  );
}

function StatCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      <p className="mt-3 text-2xl font-bold tracking-tight text-gray-900">
        {value}
      </p>

    </div>
  );
}

function ProductCard({
  title,
  subtitle,
  icon,
  products,
  positive = false,
}: {
  title: string;
  subtitle: string;
  icon: string;
  products: Product[];
  positive?: boolean;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

      <div className="border-b border-gray-100 px-6 py-5">

        <div className="flex items-center gap-3">

          <div
            className={`flex h-10 w-10 items-center justify-center rounded-xl ${
              positive
                ? "bg-green-50 text-green-600"
                : "bg-orange-50 text-orange-600"
            }`}
          >
            {icon}
          </div>

          <div>

            <h3 className="font-semibold text-gray-900">
              {title}
            </h3>

            <p className="mt-0.5 text-xs text-gray-500">
              {subtitle}
            </p>

          </div>

        </div>

      </div>

      <div className="divide-y divide-gray-100">

        {products.length === 0 ? (
          <div className="px-6 py-8 text-center text-sm text-gray-400">
            No product data available.
          </div>
        ) : (
          products.map((product, index) => (
            <div
              key={`${product.product_name}-${index}`}
              className="flex items-center justify-between px-6 py-4"
            >

              <div className="flex items-center gap-3">

                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-50 text-xs font-semibold text-gray-500">
                  {index + 1}
                </div>

                <p className="text-sm font-medium text-gray-800">
                  {product.product_name}
                </p>

              </div>

              <p className="text-sm font-semibold text-gray-900">
                ₹{Number(product.total_revenue).toLocaleString("en-IN")}
              </p>

            </div>
          ))
        )}

      </div>

    </div>
  );
}