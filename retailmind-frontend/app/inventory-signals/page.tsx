"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type InventorySignal = {
  product_name: string;
  units_sold_recently: number;
};

export default function InventorySignals() {
  const [signals, setSignals] = useState<InventorySignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadInventorySignals() {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const response = await fetch(`${API_URL}/inventory-signals`, {
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

      setSignals(result);
    } catch (err) {
      console.error(err);
      setError("Could not load inventory data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadInventorySignals();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Analyzing recent sales...
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
              loadInventorySignals();
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
            Inventory Intelligence
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Inventory Demand Signals
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Based on units sold in the last 30 days — not live stock levels.
          </p>
        </div>

        {signals.length > 0 ? (
          <>
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Fastest-Moving Products
              </h2>

              <p className="mt-1 text-sm text-gray-500">
                Products with the highest recent sales activity.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {signals.map((signal, index) => (
                <div
                  key={`${signal.product_name}-${index}`}
                  className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-xl">
                        📦
                      </div>

                      <div>
                        <p className="font-semibold text-gray-900">
                          {signal.product_name}
                        </p>

                        <p className="mt-1 text-xs text-gray-500">
                          Recent sales
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">
                        {signal.units_sold_recently}
                      </p>

                      <p className="text-xs text-gray-500">
                        units sold
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-2xl border border-blue-100 bg-blue-50 p-5">
              <p className="text-sm font-medium text-blue-900">
                💡 Stock Insight
              </p>

              <p className="mt-1 text-sm text-blue-800">
                Consider keeping extra stock of these items.
              </p>
            </div>
          </>
        ) : (
          <div className="rounded-2xl border border-gray-200 bg-white p-10 text-center shadow-sm">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-gray-50 text-2xl">
              📦
            </div>

            <h2 className="mt-4 text-lg font-semibold text-gray-900">
              No recent sales data
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              No recent sales data available yet.
            </p>
          </div>
        )}

      </div>
    </main>
  );
}