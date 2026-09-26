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
  status?: string;
  average_interval?: number;
  days_since_last_bought?: number;
  message?: string;
  error?: string;
};

type Action = {
  status?: string;
  action?: string;
  whatsapp_message?: string;
  error?: string;
};

export default function PredictionAction() {
  const [search, setSearch] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] =
    useState<Customer | null>(null);

  const [prediction, setPrediction] =
    useState<Prediction | null>(null);

  const [action, setAction] =
    useState<Action | null>(null);

  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================
  // SEARCH CUSTOMERS BY NAME
  // =========================================

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
        setError(
          "Your session has expired. Please login again."
        );
        return;
      }

      const response = await fetch(
        `${API_URL}/customer-search?name=${encodeURIComponent(
          value
        )}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      let data: any = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        setError(
          data?.error ||
            `Customer search failed: ${response.status}`
        );
        return;
      }

      const results = Array.isArray(data)
        ? data
        : data?.customers || [];

      setCustomers(results);

    } catch (err) {
      console.error(
        "Customer search error:",
        err
      );

      setError(
        "Failed to search customers."
      );

    } finally {
      setSearching(false);
    }
  }

  // =========================================
  // SELECT CUSTOMER
  // =========================================

  function selectCustomer(customer: Customer) {
    setSelectedCustomer(customer);
    setSearch(customer.name || "");
    setCustomers([]);
    setPrediction(null);
    setAction(null);
    setError("");
  }

  // =========================================
  // ANALYZE CUSTOMER
  // =========================================

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
        setError(
          "Your session has expired. Please login again."
        );
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const customerId = selectedCustomer.customer_id;

      // =========================================
      // CALL BOTH APIs
      // =========================================

      const [
        predResponse,
        actionResponse,
      ] = await Promise.all([
        fetch(
          `${API_URL}/customer/${customerId}/prediction`,
          {
            method: "GET",
            headers,
          }
        ),

        fetch(
          `${API_URL}/customer/${customerId}/next-best-action`,
          {
            method: "GET",
            headers,
          }
        ),
      ]);

      // =========================================
      // PARSE PREDICTION RESPONSE
      // =========================================

      let predData: Prediction = {};

      try {
        predData = await predResponse.json();
      } catch {
        predData = {
          error:
            "Invalid response received from prediction service.",
        };
      }

      // =========================================
      // PARSE ACTION RESPONSE
      // =========================================

      let actionData: Action = {};

      try {
        actionData = await actionResponse.json();
      } catch {
        actionData = {
          error:
            "Invalid response received from next-best-action service.",
        };
      }

      // =========================================
      // PREDICTION ERROR
      // =========================================

      if (!predResponse.ok) {
        setError(
          predData.error ||
            `Prediction request failed: ${predResponse.status}`
        );
        return;
      }

      if (predData.error) {
        setError(predData.error);
        return;
      }

      // =========================================
      // ACTION ERROR
      // =========================================

      if (!actionResponse.ok) {
        setError(
          actionData.error ||
            `Next-best-action request failed: ${actionResponse.status}`
        );
        return;
      }

      if (actionData.error) {
        setError(actionData.error);
        return;
      }

      // =========================================
      // VALIDATE PREDICTION
      // =========================================

      if (!predData.status) {
        console.error(
          "Invalid prediction response:",
          predData
        );

        setError(
          "Prediction data is incomplete for this customer."
        );

        return;
      }

      // =========================================
      // VALIDATE ACTION
      // =========================================

      if (!actionData.status) {
        console.error(
          "Invalid next-best-action response:",
          actionData
        );

        setError(
          "Next-best-action data is incomplete for this customer."
        );

        return;
      }

      // =========================================
      // SAVE RESULTS
      // =========================================

      setPrediction(predData);
      setAction(actionData);

    } catch (err) {
      console.error(
        "Prediction & Action error:",
        err
      );

      setError(
        "Failed to analyze purchase pattern. Please try again."
      );

    } finally {
      setLoading(false);
    }
  }

  // =========================================
  // FORMAT STATUS SAFELY
  // =========================================

  function formatStatus(status?: string) {
    if (!status) {
      return "Unavailable";
    }

    return status
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase());
  }

  // =========================================
  // UI
  // =========================================

  return (
    <main className="min-h-screen bg-[#f7f9fc] px-4 py-6 text-gray-900 sm:px-6 sm:py-10">

      <div className="mx-auto max-w-6xl">

        {/* =====================================
            HEADER
        ====================================== */}

        <div className="mb-8">

          <p className="text-sm font-medium text-blue-600">
            Customer Intelligence
          </p>

          <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">
            Prediction & Next Best Action
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-gray-500 sm:text-base">
            Analyze a customer's purchase pattern and
            determine the next action.
          </p>

        </div>

        {/* =====================================
            CUSTOMER SEARCH
        ====================================== */}

        <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm sm:p-6">

          <label className="block text-sm font-semibold text-gray-800">
            Select Customer
          </label>

          <div className="relative mt-3">

            <input
              type="text"
              value={search}
              onChange={(e) =>
                searchCustomers(e.target.value)
              }
              className="w-full rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="Search customer by name..."
            />

            {/* Searching */}

            {searching && (
              <p className="mt-2 text-xs text-gray-500">
                Searching customers...
              </p>
            )}

            {/* =================================
                CUSTOMER SUGGESTIONS
            ================================== */}

            {customers.length > 0 &&
              !selectedCustomer && (

                <div className="absolute left-0 right-0 z-30 mt-2 max-h-64 overflow-y-auto rounded-xl border border-gray-200 bg-white shadow-xl">

                  {customers.map((customer) => (

                    <button
                      key={customer.customer_id}
                      type="button"
                      onClick={() =>
                        selectCustomer(customer)
                      }
                      className="block w-full border-b border-gray-100 px-4 py-3 text-left transition last:border-b-0 hover:bg-gray-50"
                    >

                      <p className="text-sm font-semibold text-gray-900">
                        {customer.name ||
                          "Unnamed Customer"}
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

          {/* =====================================
              SELECTED CUSTOMER
          ====================================== */}

          {selectedCustomer && (

            <div className="mt-4 flex flex-col gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <p className="text-sm font-semibold text-blue-900">
                  {selectedCustomer.name ||
                    "Unnamed Customer"}
                </p>

                {selectedCustomer.phone && (
                  <p className="mt-1 text-xs text-blue-700">
                    {selectedCustomer.phone}
                  </p>
                )}

              </div>

              <button
                type="button"
                onClick={() => {
                  setSelectedCustomer(null);
                  setSearch("");
                  setCustomers([]);
                  setPrediction(null);
                  setAction(null);
                  setError("");
                }}
                className="self-start text-xs font-semibold text-blue-700 hover:text-blue-900 sm:self-auto"
              >
                Change
              </button>

            </div>
          )}

          {/* =====================================
              ANALYZE BUTTON
          ====================================== */}

          <button
            type="button"
            onClick={getPredictionAndAction}
            disabled={loading || !selectedCustomer}
            className="mt-5 w-full rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Analyzing..."
              : "Get Prediction & Action"}
          </button>

        </section>

        {/* =====================================
            ERROR
        ====================================== */}

        {error && (

          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">

            <p className="font-semibold">
              Unable to analyze customer
            </p>

            <p className="mt-1">
              {error}
            </p>

          </div>
        )}

        {/* =====================================
            PREDICTION
        ====================================== */}

        {prediction && (

          <>

            {prediction.status ===
            "not_enough_data" ? (

              <div className="mt-8 rounded-2xl border border-amber-200 bg-amber-50 p-6">

                <h2 className="font-semibold text-amber-900">
                  Not Enough Purchase History
                </h2>

                <p className="mt-2 text-sm text-amber-800">
                  Not enough purchase history yet for
                  this customer (need at least 2 invoices).
                </p>

              </div>

            ) : (

              <section className="mt-8">

                <h2 className="mb-4 text-xl font-bold">
                  Purchase Prediction
                </h2>

                <div className="grid gap-4 md:grid-cols-3">

                  {/* Average Interval */}

                  <StatCard
                    title="Avg. Purchase Interval"
                    value={
                      prediction.average_interval !==
                        undefined &&
                      prediction.average_interval !== null
                        ? `${Number(
                            prediction.average_interval
                          ).toFixed(1)} days`
                        : "Unavailable"
                    }
                  />

                  {/* Days Since Last Purchase */}

                  <StatCard
                    title="Days Since Last Purchase"
                    value={
                      prediction.days_since_last_bought !==
                        undefined &&
                      prediction.days_since_last_bought !== null
                        ? String(
                            prediction.days_since_last_bought
                          )
                        : "Unavailable"
                    }
                  />

                  {/* Status */}

                  <StatCard
                    title="Status"
                    value={formatStatus(
                      prediction.status
                    )}
                  />

                </div>

                {/* Prediction Message */}

                {prediction.message && (

                  <div className="mt-5 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-sm text-blue-900">
                    {prediction.message}
                  </div>

                )}

              </section>
            )}

          </>
        )}

        {/* =====================================
            NEXT BEST ACTION
        ====================================== */}

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

              {/* =================================
                  WHATSAPP MESSAGE
              ================================== */}

              {action.whatsapp_message && (

                <div className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

                  <div className="mb-4">

                    <h3 className="font-semibold text-gray-900">
                      📱 Suggested WhatsApp Message
                    </h3>

                    <p className="mt-1 text-xs text-gray-500">
                      Copy this message and send it
                      to the customer.
                    </p>

                  </div>

                  <textarea
                    readOnly
                    value={
                      action.whatsapp_message
                    }
                    rows={5}
                    className="w-full resize-none rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800 outline-none"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      navigator.clipboard.writeText(
                        action.whatsapp_message || ""
                      )
                    }
                    className="mt-4 rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800"
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

/* =========================================
   STAT CARD
========================================= */

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

      <p className="mt-3 text-2xl font-bold tracking-tight text-gray-900">
        {value}
      </p>

    </div>
  );
}