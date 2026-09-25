"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

type SearchResult = {
  customer_id: number;
  name: string;
  phone: string;
};

type CustomerData = {
  customer: {
    name: string | null;
    phone: string | null;
    customer_type: string | null;
    bargains: string | null;
    payment_mode: string | null;
    preference_tier: string | null;
    buying_behavior: string | null;
    free_note: string | null;
  };
  order_count: number;
  total_spend: number;
  average_order_value: number;
  outstanding_credit: number;
  last_purchase: string;
  favorite_products: {
    product_name: string;
    total_quantity: number;
  }[];
};

export default function CustomerProfile() {
  const [searchType, setSearchType] = useState<"phone" | "name">("phone");
  const [searchValue, setSearchValue] = useState("");

  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] =
    useState<number | null>(null);

  const [customerData, setCustomerData] =
    useState<CustomerData | null>(null);

  const [searching, setSearching] = useState(false);
  const [loadingCustomer, setLoadingCustomer] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function getToken() {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    return session?.access_token;
  }

  // Name autocomplete only
  async function searchNameSuggestions(value: string) {
    if (searchType !== "name" || value.trim().length < 2) {
      setResults([]);
      return;
    }

    try {
      const token = await getToken();

      if (!token) {
        setResults([]);
        return;
      }

      const response = await fetch(
        `${API_URL}/customer-search?name=${encodeURIComponent(value.trim())}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        setResults([]);
        return;
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setResults(data);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error("Name suggestion error:", err);
      setResults([]);
    }
  }

  async function searchCustomer() {
    if (!searchValue.trim()) {
      setError("Please enter a name or phone number.");
      return;
    }

    setSearching(true);
    setError("");
    setMessage("");
    setResults([]);
    setSelectedCustomerId(null);
    setCustomerData(null);

    try {
      const token = await getToken();

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const params = new URLSearchParams();

      if (searchType === "phone") {
        params.set("phone", searchValue.trim());
      } else {
        params.set("name", searchValue.trim());
      }

      const response = await fetch(
        `${API_URL}/customer-search?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(`Search failed: ${response.status}`);
        return;
      }

      if (data?.error) {
        setError(data.error);
        return;
      }

      if (!data || data.length === 0) {
        setError("Customer not found.");
        return;
      }

      setResults(data);

      if (data.length === 1) {
        loadCustomer(data[0].customer_id);
      }
    } catch (err) {
      console.error(err);
      setError("Failed to search customer.");
    } finally {
      setSearching(false);
    }
  }

  async function loadCustomer(customerId: number) {
    setSelectedCustomerId(customerId);
    setLoadingCustomer(true);
    setError("");
    setMessage("");
    setResults([]);

    try {
      const token = await getToken();

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const response = await fetch(
        `${API_URL}/customer/${customerId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(`Request failed: ${response.status}`);
        return;
      }

      if (data?.error) {
        setError(data.error);
        return;
      }

      setCustomerData(data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch customer data.");
    } finally {
      setLoadingCustomer(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f9fc] px-6 py-10 text-gray-900">
      <div className="mx-auto max-w-7xl">

        {/* Header */}
        <div className="mb-8">
          <p className="text-sm font-medium text-blue-600">
            Customer Intelligence
          </p>

          <h1 className="mt-1 text-3xl font-bold tracking-tight">
            Customer Profile
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Search and understand your customers using their purchase history.
          </p>
        </div>

        {/* Search */}
        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

          <div className="mb-5">
            <p className="text-sm font-semibold text-gray-800">
              Search customer by
            </p>

            <div className="mt-3 flex gap-3">

              {/* Phone */}
              <button
                onClick={() => {
                  setSearchType("phone");
                  setSearchValue("");
                  setResults([]);
                  setCustomerData(null);
                  setError("");
                  setMessage("");
                }}
                className={`rounded-lg px-4 py-2 text-sm font-medium ${
                  searchType === "phone"
                    ? "bg-blue-600 text-white"
                    : "border border-gray-200 bg-white text-gray-600"
                }`}
              >
                Phone Number
              </button>

              {/* Name */}
              <button
                onClick={() => {
                  setSearchType("name");
                  setSearchValue("");
                  setResults([]);
                  setCustomerData(null);
                  setError("");
                  setMessage("");
                }}
                className={`rounded-lg px-4 py-2 text-sm font-medium ${
                  searchType === "name"
                    ? "bg-blue-600 text-white"
                    : "border border-gray-200 bg-white text-gray-600"
                }`}
              >
                Name
              </button>

            </div>
          </div>

          <div className="relative">

            <div className="flex gap-3">

              <input
                value={searchValue}
                onChange={(e) => {
                  const value = e.target.value;

                  setSearchValue(value);
                  setError("");
                  setMessage("");

                  // ONLY name search gets suggestions
                  if (searchType === "name") {
                    searchNameSuggestions(value);
                  } else {
                    // Phone search stays unchanged
                    setResults([]);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    searchCustomer();
                  }
                }}
                placeholder={
                  searchType === "phone"
                    ? "Enter customer phone number"
                    : "Enter customer name"
                }
                className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <button
                onClick={searchCustomer}
                disabled={searching}
                className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {searching ? "Searching..." : "Search Customer"}
              </button>

            </div>

            {/* Name Suggestions */}
            {searchType === "name" && results.length > 0 && (
              <div className="absolute left-0 right-[150px] top-full z-50 mt-2 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">

                {results.map((customer) => (
                  <button
                    key={customer.customer_id}
                    onClick={() => {
                      setSearchValue(customer.name);
                      setResults([]);
                      loadCustomer(customer.customer_id);
                    }}
                    className="flex w-full items-center justify-between border-b border-gray-100 px-4 py-3 text-left last:border-b-0 hover:bg-blue-50"
                  >
                    <div>
                      <p className="font-semibold text-gray-900">
                        {customer.name || "Unknown"}
                      </p>

                      <p className="mt-1 text-sm text-gray-500">
                        {customer.phone || "No phone"}
                      </p>
                    </div>

                    <span className="text-sm font-medium text-blue-600">
                      View →
                    </span>
                  </button>
                ))}

              </div>
            )}

          </div>
        </section>

        {/* Multiple Results for manual search */}
        {searchType === "phone" && results.length > 1 && (
          <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

            <h2 className="text-lg font-semibold">
              Customers Found
            </h2>

            <div className="mt-4 space-y-2">

              {results.map((customer) => (
                <button
                  key={customer.customer_id}
                  onClick={() => loadCustomer(customer.customer_id)}
                  className={`flex w-full items-center justify-between rounded-xl border p-4 text-left transition hover:border-blue-300 hover:bg-blue-50 ${
                    selectedCustomerId === customer.customer_id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200"
                  }`}
                >
                  <div>

                    <p className="font-semibold text-gray-900">
                      {customer.name || "Unknown"}
                    </p>

                    <p className="mt-1 text-sm text-gray-500">
                      {customer.phone || "No phone"}
                    </p>

                  </div>

                  <span className="text-sm font-medium text-blue-600">
                    View Profile →
                  </span>
                </button>
              ))}

            </div>
          </section>
        )}

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Message */}
        {message && (
          <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
            {message}
          </div>
        )}

        {/* Loading */}
        {loadingCustomer && (
          <div className="mt-8 rounded-2xl border border-gray-200 bg-white p-10 text-center shadow-sm">

            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />

            <p className="mt-4 text-sm text-gray-500">
              Fetching customer data...
            </p>

          </div>
        )}

        {/* Customer Profile */}
        {customerData && !loadingCustomer && (
          <div className="mt-8">

            {/* Profile */}
            <section className="rounded-2xl border border-gray-200 bg-white p-7 shadow-sm">

              <div className="flex items-center gap-4">

                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-xl font-bold text-blue-700">
                  {(customerData.customer.name || "U")
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <div>

                  <h2 className="text-2xl font-bold">
                    {customerData.customer.name || "Unknown"}
                  </h2>

                  <p className="mt-1 text-sm text-gray-500">
                    {customerData.customer.phone || "No phone number"}
                  </p>

                </div>

              </div>

              <div className="mt-7 grid gap-5 md:grid-cols-2">

                <Info
                  label="Customer Type"
                  value={customerData.customer.customer_type}
                />

                <Info
                  label="Bargains"
                  value={customerData.customer.bargains}
                />

                <Info
                  label="Payment Mode"
                  value={customerData.customer.payment_mode}
                />

                <Info
                  label="Preference Tier"
                  value={customerData.customer.preference_tier}
                />

                <Info
                  label="Buying Behavior"
                  value={customerData.customer.buying_behavior}
                />

                <Info
                  label="Note"
                  value={customerData.customer.free_note}
                  full
                />

              </div>

            </section>

            {/* Metrics */}
            <section className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">

              <StatCard
                title="Total Orders"
                value={customerData.order_count.toLocaleString("en-IN")}
              />

              <StatCard
                title="Total Spend"
                value={`₹${Number(
                  customerData.total_spend
                ).toLocaleString("en-IN")}`}
              />

              <StatCard
                title="Avg Order Value"
                value={`₹${Number(
                  customerData.average_order_value
                ).toLocaleString("en-IN", {
                  maximumFractionDigits: 2,
                })}`}
              />

              <StatCard
                title="Outstanding Credit"
                value={`₹${Number(
                  customerData.outstanding_credit
                ).toLocaleString("en-IN")}`}
              />

            </section>

            {/* Last Purchase */}
            <section className="mt-6 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">

              <p className="text-sm font-medium text-gray-500">
                Last Purchase
              </p>

              <p className="mt-2 text-lg font-semibold text-gray-900">
                {customerData.last_purchase || "No purchase recorded"}
              </p>

            </section>

            {/* Favorite Products */}
            <section className="mt-6 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">

              <div className="border-b border-gray-100 px-6 py-5">

                <h2 className="font-semibold text-gray-900">
                  Favorite Products
                </h2>

                <p className="mt-1 text-xs text-gray-500">
                  Products this customer buys most frequently
                </p>

              </div>

              {customerData.favorite_products.length === 0 ? (
                <div className="px-6 py-8 text-center text-sm text-gray-400">
                  No favorite product data available.
                </div>
              ) : (
                <div className="divide-y divide-gray-100">

                  {customerData.favorite_products.map(
                    (product, index) => (
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
                          {product.total_quantity} units
                        </p>

                      </div>
                    )
                  )}

                </div>
              )}

            </section>

          </div>
        )}

      </div>
    </main>
  );
}

function Info({
  label,
  value,
  full = false,
}: {
  label: string;
  value: string | null;
  full?: boolean;
}) {
  return (
    <div className={full ? "md:col-span-2" : ""}>

      <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-medium text-gray-800">
        {value || "Not set"}
      </p>

    </div>
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