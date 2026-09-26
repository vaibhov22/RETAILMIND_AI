"use client";

import { useEffect, useState } from "react";
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

  function handleRefresh() {
    setRefreshing(true);
    loadDashboard();
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f7f9fc] px-6">
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
      <main className="flex min-h-screen items-center justify-center bg-[#f7f9fc] px-6">
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
            disabled={refreshing}
            className="mt-6 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
          >
            {refreshing ? "Trying..." : "Try Again"}
          </button>
        </div>
      </main>
    );
  }

  const { summary, hero_products, weak_products } = data;

  return (
    <main className="min-h-screen bg-[#f7f9fc] text-gray-900">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">

        {/* =========================
            PAGE HEADING
        ========================== */}
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-blue-600">
              Business Overview
            </p>

            <h1 className="mt-1 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Dashboard
            </h1>

            <p className="mt-2 max-w-xl text-sm text-gray-500 sm:text-base">
              Monitor your store performance and product activity.
            </p>
          </div>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="shrink-0 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 sm:px-4"
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* =========================
            OVERVIEW CARDS
        ========================== */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 lg:gap-5">

          <StatCard
            title="Total Revenue"
            value={`₹${Number(summary.total_revenue).toLocaleString(
              "en-IN"
            )}`}
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

        {/* =========================
            PRODUCTS
        ========================== */}
        <section className="mt-6 grid gap-5 lg:mt-8 lg:grid-cols-2 lg:gap-6">

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

/* =========================
   STAT CARD
========================= */

function StatCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm sm:p-6">
      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      <p className="mt-3 text-2xl font-bold tracking-tight text-gray-900 sm:text-3xl">
        {value}
      </p>
    </div>
  );
}

/* =========================
   PRODUCT CARD
========================= */

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

      {/* Card Header */}
      <div className="border-b border-gray-100 px-5 py-5 sm:px-6">
        <div className="flex items-center gap-3">

          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
              positive
                ? "bg-green-50 text-green-600"
                : "bg-orange-50 text-orange-600"
            }`}
          >
            {icon}
          </div>

          <div className="min-w-0">
            <h2 className="font-semibold text-gray-900">
              {title}
            </h2>

            <p className="mt-0.5 text-xs text-gray-500">
              {subtitle}
            </p>
          </div>

        </div>
      </div>

      {/* Products */}
      <div className="divide-y divide-gray-100">

        {products.length === 0 ? (
          <div className="px-6 py-8 text-center text-sm text-gray-400">
            No product data available.
          </div>
        ) : (
          products.map((product, index) => (
            <div
              key={`${product.product_name}-${index}`}
              className="flex items-center justify-between gap-4 px-5 py-4 sm:px-6"
            >

              <div className="flex min-w-0 items-center gap-3">

                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-50 text-xs font-semibold text-gray-500">
                  {index + 1}
                </div>

                <p className="truncate text-sm font-medium text-gray-800">
                  {product.product_name}
                </p>

              </div>

              <p className="shrink-0 text-sm font-semibold text-gray-900">
                ₹
                {Number(product.total_revenue).toLocaleString(
                  "en-IN"
                )}
              </p>

            </div>
          ))
        )}

      </div>
    </div>
  );
}