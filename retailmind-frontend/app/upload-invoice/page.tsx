"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";

const API_URL = "https://retailmind-ai-7h7v.onrender.com";

export default function UploadInvoicePage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [newCustomerId, setNewCustomerId] = useState<number | null>(null);

  const [customerType, setCustomerType] = useState("Regular");
  const [bargains, setBargains] = useState("Never");
  const [paymentMode, setPaymentMode] = useState("Cash");
  const [preferenceTier, setPreferenceTier] = useState("Budget");
  const [buyingBehavior, setBuyingBehavior] =
    useState("Planned purchases");
  const [freeNote, setFreeNote] = useState("");

  const [savingProfile, setSavingProfile] = useState(false);

  const handleFileChange = (selectedFile: File | null) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setMessage("");
    setError("");
  };

  const processInvoice = async () => {
    if (!file) return;

    setProcessing(true);
    setMessage("");
    setError("");

    try {
      const { data } = await supabase.auth.getSession();

      const token = data.session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_URL}/upload-invoice`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const result = await response.json();

      if (!response.ok) {
        setError(`Request failed: ${response.status}`);
        return;
      }

      if (result.error) {
        setError(`Something went wrong: ${result.error}`);
        return;
      }

      setMessage(result.message);

      if (result.needs_profile_questions) {
        setNewCustomerId(result.customer_id);
      } else {
        setNewCustomerId(null);
      }
    } catch (err) {
      setError("Failed to process invoice.");
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  const saveProfile = async () => {
    if (!newCustomerId) return;

    setSavingProfile(true);
    setMessage("");
    setError("");

    try {
      const { data } = await supabase.auth.getSession();

      const token = data.session?.access_token;

      if (!token) {
        setError("Your session has expired. Please login again.");
        return;
      }

      const payload = {
        customer_id: newCustomerId,
        customer_type: customerType,
        bargains,
        payment_mode: paymentMode,
        preference_tier: preferenceTier,
        buying_behavior: buyingBehavior,
        free_note: freeNote,
      };

      const response = await fetch(
        `${API_URL}/update-customer-profile`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        setError("Failed to save profile.");
        return;
      }

      setMessage(result.message || "Customer profile saved!");
      setNewCustomerId(null);
      setFreeNote("");
    } catch (err) {
      setError("Failed to save customer profile.");
      console.error(err);
    } finally {
      setSavingProfile(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-5xl">

        <div className="mb-8">
          <p className="text-sm font-medium text-blue-600">
            Invoice Processing
          </p>

          <h1 className="mt-1 text-4xl font-bold text-slate-900">
            Upload Invoice
          </h1>

          <p className="mt-2 text-slate-500">
            Upload an invoice image and RetailMind AI will extract
            and save the information automatically.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

          <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center transition hover:border-blue-400 hover:bg-blue-50">

            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 text-2xl">
              📤
            </div>

            <p className="text-lg font-semibold text-slate-800">
              Choose invoice image
            </p>

            <p className="mt-1 text-sm text-slate-500">
              PNG, JPG or JPEG
            </p>

            <input
              type="file"
              accept="image/png,image/jpeg"
              className="hidden"
              onChange={(e) =>
                handleFileChange(e.target.files?.[0] || null)
              }
            />
          </label>

          {preview && (
            <div className="mt-8">
              <p className="mb-3 text-sm font-semibold text-slate-700">
                Invoice Preview
              </p>

              <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                <img
                  src={preview}
                  alt="Invoice preview"
                  className="max-h-[500px] w-full object-contain"
                />
              </div>
            </div>
          )}

          {file && (
            <button
              onClick={processInvoice}
              disabled={processing}
              className="mt-6 w-full rounded-xl bg-blue-600 px-6 py-3.5 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {processing
                ? "Reading invoice with AI..."
                : "Process Invoice"}
            </button>
          )}

          {message && (
            <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-4 text-green-700">
              {message}
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
              {error}
            </div>
          )}
        </div>

        {newCustomerId && (
          <div className="mt-8 rounded-2xl border border-amber-200 bg-white p-8 shadow-sm">

            <div className="mb-6">
              <p className="text-sm font-medium text-amber-600">
                New Customer
              </p>

              <h2 className="mt-1 text-2xl font-bold text-slate-900">
                Quick Customer Profile
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Answer a few questions to help RetailMind understand
                this customer better.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Customer type
                </label>

                <select
                  value={customerType}
                  onChange={(e) => setCustomerType(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >
                  <option>Regular</option>
                  <option>Occasional</option>
                  <option>New</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  How often do they bargain?
                </label>

                <select
                  value={bargains}
                  onChange={(e) => setBargains(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >
                  <option>Never</option>
                  <option>Sometimes</option>
                  <option>Often</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Preferred payment method
                </label>

                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >
                  <option>Cash</option>
                  <option>UPI</option>
                  <option>Credit</option>
                  <option>Mixed</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Preferred product range
                </label>

                <select
                  value={preferenceTier}
                  onChange={(e) => setPreferenceTier(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >
                  <option>Budget</option>
                  <option>Mid-range</option>
                  <option>Premium</option>
                  <option>Not sure</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Buying behavior
                </label>

                <select
                  value={buyingBehavior}
                  onChange={(e) => setBuyingBehavior(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >
                  <option>Planned purchases</option>
                  <option>Impulse purchases</option>
                  <option>Mix of both</option>
                  <option>Not sure</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Anything else important? (optional)
                </label>

                <textarea
                  value={freeNote}
                  onChange={(e) => setFreeNote(e.target.value)}
                  rows={4}
                  placeholder="Add any useful customer information..."
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

            </div>

            <button
              onClick={saveProfile}
              disabled={savingProfile}
              className="mt-6 w-full rounded-xl bg-slate-900 px-6 py-3.5 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingProfile ? "Saving Profile..." : "Save Profile"}
            </button>

          </div>
        )}

      </div>
    </main>
  );
}