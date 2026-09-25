"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type Customer = {
  customer_id: number;
  name?: string;
  phone?: string;
};

type Prediction = {
  status: string;
  average_interval?: number;
  days_since_last_bought?: number;
  message?: string;
};

type Action = {
  status: string;
  action?: string;
  whatsapp_message?: string;
};

export default function PredictionAction() {
  const [search, setSearch] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] =
    useState<Customer | null>(null);

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [action, setAction] = useState<Action | null>(null);

  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function searchCustomers(value: string) {
    setSearch(value);
    setSelectedCustomer(null);
    setPrediction(null);
    setAction(null);
    setError("");

    if (!value.trim()) {
      setCustomers([]);
      return;
    }

    try {
      setSearching(true);

      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const response = await fetch(
        `${API_URL}/customer-search?name=${encodeURIComponent(value)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(`Customer search failed: ${response.status}`);
        return;
      }

      setCustomers(Array.isArray(data) ? data : data.customers || []);
    } catch (err) {
      console.error(err);
      setError("Failed to search customers.");
    } finally {
      setSearching(false);
    }
  }

  async function getPredictionAndAction() {
    if (!selectedCustomer) {
      setError("Please select a customer first.");
      return;
    }

    setLoading(true);
    setError("");
    setPrediction(null);
    setAction(null);

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const customerId = selectedCustomer.customer_id;

      const [predResponse, actionResponse] = await Promise.all([
        fetch(`${API_URL}/customer/${customerId}/prediction`, {
          headers,
        }),
        fetch(`${API_URL}/customer/${customerId}/next-best-action`, {
          headers,
        }),
      ]);

      const predData = await predResponse.json();
      const actionData = await actionResponse.json();

      if (!predResponse.ok) {
        setError(`Prediction request failed: ${predResponse.status}`);
        return;
      }

      if (!actionResponse.ok) {
        setError(
          `Next-best-action request failed: ${actionResponse.status}`
        );
        return;
      }

      setPrediction(predData);
      setAction(actionData);
    } catch (err) {
      console.error(err);
      setError("Failed to analyze purchase pattern.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] px-6 py-10 text-gray-900">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-8">
          <p className="text-sm font-medium text-blue-600">
            Customer Intelligence
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Prediction & Next Best Action
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Analyze a customer's purchase pattern and determine the next action.
          </p>
        </div>

        {/* Customer Search */}
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <label className="block text-sm font-semibold text-gray-800">
            Select Customer
          </label>

          <div className="relative mt-3">
            <input
              type="text"
              value={search}
              onChange={(e) => searchCustomers(e.target.value)}
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="Search customer by name or phone..."
            />

            {searching && (
              <p className="mt-2 text-xs text-gray-500">
                Searching...
              </p>
            )}

            {customers.length > 0 && !selectedCustomer && (
              <div className="absolute left-0 right-0 z-20 mt-2 max-h-64 overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-lg">

                {customers.map((customer) => (
                  <button
                    key={customer.customer_id}
                    onClick={() => {
                      setSelectedCustomer(customer);
                      setSearch(customer.name || customer.phone || "");
                      setCustomers([]);
                      setError("");
                    }}
                    className="block w-full border-b border-gray-100 px-4 py-3 text-left hover:bg-gray-50"
                  >
                    <p className="text-sm font-semibold text-gray-900">
                      {customer.name || "Unnamed Customer"}
                    </p>

                    {customer.phone && (
                      <p className="mt-1 text-xs text-gray-500">
                        {customer.phone}
                      </p>
                    )}
                  </button>
                ))}

              </div>
            )}
          </div>

          {/* Selected Customer */}
          {selectedCustomer && (
            <div className="mt-4 flex items-center justify-between rounded-xl border border-blue-200 bg-blue-50 p-4">

              <div>
                <p className="text-sm font-semibold text-blue-900">
                  {selectedCustomer.name || "Unnamed Customer"}
                </p>

                {selectedCustomer.phone && (
                  <p className="mt-1 text-xs text-blue-700">
                    {selectedCustomer.phone}
                  </p>
                )}
              </div>

              <button
                onClick={() => {
                  setSelectedCustomer(null);
                  setSearch("");
                  setPrediction(null);
                  setAction(null);
                }}
                className="text-xs font-semibold text-blue-700 hover:text-blue-900"
              >
                Change
              </button>

            </div>
          )}

          <button
            onClick={getPredictionAndAction}
            disabled={loading || !selectedCustomer}
            className="mt-5 w-full rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Analyzing..."
              : "Get Prediction & Action"}
          </button>

        </section>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Prediction */}
        {prediction && (
          <>
            {prediction.status === "not_enough_data" ? (
              <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-6">
                <h2 className="font-semibold text-amber-900">
                  Not Enough Purchase History
                </h2>

                <p className="mt-2 text-sm text-amber-800">
                  Not enough purchase history yet for this customer
                  (need at least 2 invoices).
                </p>
              </div>
            ) : (
              <section className="mt-8">

                <h2 className="mb-4 text-xl font-bold">
                  Purchase Prediction
                </h2>

                <div className="grid gap-5 md:grid-cols-3">

                  <StatCard
                    title="Avg. Purchase Interval"
                    value={`${Number(
                      prediction.average_interval
                    ).toFixed(1)} days`}
                  />

                  <StatCard
                    title="Days Since Last Purchase"
                    value={String(
                      prediction.days_since_last_bought
                    )}
                  />

                  <StatCard
                    title="Status"
                    value={prediction.status
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (c) => c.toUpperCase())}
                  />

                </div>

                {prediction.message && (
                  <div className="mt-5 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-sm text-blue-900">
                    {prediction.message}
                  </div>
                )}

              </section>
            )}
          </>
        )}

        {/* Next Best Action */}
        {action &&
          action.status !== "not_enough_data" &&
          action.action && (
            <section className="mt-8">

              <h2 className="mb-4 text-xl font-bold">
                Recommended Action
              </h2>

              <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <p className="text-base font-medium text-gray-800">
                  {action.action}
                </p>
              </div>

              {action.whatsapp_message && (
                <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-900">
                      📱 Suggested WhatsApp Message
                    </h3>

                    <p className="mt-1 text-xs text-gray-500">
                      Copy this message and send it to the customer.
                    </p>
                  </div>

                  <textarea
                    readOnly
                    value={action.whatsapp_message}
                    rows={5}
                    className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800 outline-none"
                  />

                  <button
                    onClick={() =>
                      navigator.clipboard.writeText(
                        action.whatsapp_message || ""
                      )
                    }
                    className="mt-4 rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-800"
                  >
                    Copy Message
                  </button>

                </div>
              )}

            </section>
          )}

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