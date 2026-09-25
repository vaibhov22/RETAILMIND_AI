"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type Bundle = {
  product_1: string;
  product_2: string;
  times_bought_together: number;
};

export default function ProductBundles() {
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadBundles() {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const response = await fetch(`${API_URL}/product-bundles`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      if (result.error) {
        throw new Error(result.error);
      }

      setBundles(result);
    } catch (err) {
      console.error(err);
      setError("Could not load bundle data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBundles();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Analyzing purchase patterns...
          </p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center px-6">
        <div className="w-full max-w-md rounded-2xl border border-red-200 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600">
            !
          </div>

          <h1 className="mt-4 text-lg font-semibold text-gray-900">
            Something went wrong
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            {error}
          </p>

          <button
            onClick={() => {
              setLoading(true);
              setError("");
              loadBundles();
            }}
            className="mt-6 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] px-6 py-10 text-gray-900">
      <div className="mx-auto max-w-6xl">

        <div className="mb-8">
          <p className="text-sm font-medium text-blue-600">
            Sales Intelligence
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Product Bundle Suggestions
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Products that customers frequently buy together.
          </p>
        </div>

        {bundles.length > 0 ? (
          <div className="grid gap-5 md:grid-cols-2">
            {bundles.map((bundle, index) => (
              <div
                key={`${bundle.product_1}-${bundle.product_2}-${index}`}
                className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                    🔗
                  </div>

                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
                      Frequently Bought Together
                    </p>

                    <p className="mt-1 text-base font-semibold text-gray-900">
                      Bundle #{index + 1}
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex items-center gap-3">
                  <div className="flex-1 rounded-xl bg-gray-50 px-4 py-4 text-center">
                    <p className="text-sm font-semibold text-gray-900">
                      {bundle.product_1}
                    </p>
                  </div>

                  <span className="text-lg font-bold text-gray-400">
                    +
                  </span>

                  <div className="flex-1 rounded-xl bg-gray-50 px-4 py-4 text-center">
                    <p className="text-sm font-semibold text-gray-900">
                      {bundle.product_2}
                    </p>
                  </div>
                </div>

                <div className="mt-5 border-t border-gray-100 pt-4">
                  <p className="text-sm text-gray-500">
                    Bought together
                  </p>

                  <p className="mt-1 text-2xl font-bold text-gray-900">
                    {bundle.times_bought_together}
                    <span className="ml-2 text-sm font-medium text-gray-500">
                      times
                    </span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-blue-100 bg-blue-50 p-8 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-white text-2xl shadow-sm">
              🔗
            </div>

            <h2 className="mt-4 text-lg font-semibold text-gray-900">
              Not enough data yet
            </h2>

            <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-gray-600">
              Upload more invoices with overlapping products to discover
              bundle patterns.
            </p>
          </div>
        )}

      </div>
    </main>
  );
}