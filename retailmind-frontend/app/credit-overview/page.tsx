"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type CreditCustomer = {
  name: string;
  phone: string;
  total_credit: number;
};

type CreditData = {
  total_outstanding: number;
  customers: CreditCustomer[];
};

export default function CreditOverview() {
  const [data, setData] = useState<CreditData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadCreditData() {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const token = session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const response = await fetch(`${API_URL}/credit-overview`, {
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

      setData(result);
    } catch (err) {
      console.error(err);
      setError("Could not load credit data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCreditData();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#f7f9fc] flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Loading credit data...
          </p>
        </div>
      </main>
    );
  }

  if (error || !data) {
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
            {error || "Could not load credit data."}
          </p>

          <button
            onClick={() => {
              setLoading(true);
              setError("");
              loadCreditData();
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
            Credit Management
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Credit / Udhaar Overview
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Monitor outstanding customer credit and udhaar.
          </p>
        </div>

        <section className="rounded-2xl border border-gray-200 bg-white p-7 shadow-sm">
          <p className="text-sm font-medium text-gray-500">
            Total Outstanding Credit
          </p>

          <p className="mt-3 text-4xl font-bold tracking-tight text-gray-900">
            ₹{Number(data.total_outstanding).toLocaleString("en-IN")}
          </p>
        </section>

        {data.customers.length > 0 ? (
          <section className="mt-8 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

            <div className="border-b border-gray-100 px-6 py-5">
              <h2 className="font-semibold text-gray-900">
                Customers with Outstanding Credit
              </h2>

              <p className="mt-1 text-xs text-gray-500">
                Customers who currently have outstanding udhaar.
              </p>
            </div>

            <div className="divide-y divide-gray-100">
              {data.customers.map((customer, index) => (
                <div
                  key={`${customer.phone}-${index}`}
                  className="flex items-center justify-between px-6 py-5"
                >
                  <div>
                    <p className="font-semibold text-gray-900">
                      {customer.name}
                    </p>

                    <p className="mt-1 text-sm text-gray-500">
                      {customer.phone}
                    </p>
                  </div>

                  <p className="text-lg font-semibold text-gray-900">
                    ₹
                    {Number(customer.total_credit).toLocaleString(
                      "en-IN"
                    )}
                  </p>
                </div>
              ))}
            </div>

          </section>
        ) : (
          <div className="mt-8 rounded-2xl border border-green-200 bg-green-50 p-6 text-center">
            <p className="font-semibold text-green-800">
              No outstanding credit right now!
            </p>
          </div>
        )}

      </div>
    </main>
  );
}