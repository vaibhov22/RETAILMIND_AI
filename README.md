# RetailMind AI

### From Data → Decisions → Actions

RetailMind AI is an AI-powered business intelligence platform for small retailers that transforms invoices into persistent customer intelligence, predicts what customers may need next, and recommends the next best business action — with **zero manual data entry**.

Built for the **AI Builders Hackathon 2026**.

---

## The Problem

Small retailers — kirana stores, grocery shops, independent sellers — generate hundreds of invoices full of valuable customer and transaction data. But that data is trapped on paper or in disconnected receipts, and never becomes usable business intelligence. Retailers don't have the time or tools to manually analyze it.

## The Solution

**Scan an invoice. RetailMind does the rest.**

```
Invoice Image → AI Extraction → Validation → Database → Customer Intelligence
                                                              ↓
                                          Prediction → Next Best Action → Business Dashboard
```

The retailer never manually enters a customer, product, or transaction. The system reads the invoice, identifies the customer, updates their purchase history, learns their buying patterns, and proactively recommends actions — all grounded in real transaction data, never invented by AI.

---

## Core Features

- **AI Invoice Extraction** — upload a photo of an invoice; a vision LLM reads it (even handwritten bills) and extracts structured data
- **Automatic Customer & Product Matching** — no duplicate records; existing customers/products are recognized automatically
- **New Customer Profiling** — a short 5-question form captures behavioral context an invoice can never provide (bargaining habits, payment preference, buying style)
- **Customer Intelligence** — lifetime spend, order frequency, favorite products, outstanding credit — calculated live, always accurate
- **Next-Purchase Prediction** — learns each customer's typical purchase interval and flags when they're due, approaching, or overdue
- **Next Best Action** — recommends a concrete action and generates a ready-to-send WhatsApp message, personalized with real purchase history
- **Business Dashboard** — store-wide revenue, hero products, weak/slow-moving products
- **Credit (Udhaar) Intelligence** — tracks outstanding customer credit across the business
- **Product Bundling Insights** — surfaces products frequently bought together, from real transaction co-occurrence
- **Inventory Demand Signals** — flags fast-moving products based on recent sales velocity
- **Retailer Copilot** — ask any business question in plain English; an AI agent calls the right internal tools to fetch real data and explain it in natural language, with conversation memory

**Design principle:** AI is only ever used to *extract* and *explain* — every number, prediction, and recommendation is grounded in real calculations against real transaction data. The AI never invents facts about the business.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Validation | Pydantic |
| AI — Vision (invoice extraction) | Groq (Qwen vision model) |
| AI — Text (explanations, copilot, prediction messages) | Groq (GPT-OSS 120B) |
| Frontend | Streamlit |
| Language | Python |

---

## Project Structure

```
RETAILMIND_AI/
├── app/                        # Backend
│   ├── main.py                 # FastAPI routes
│   ├── database.py             # DB engine/session setup
│   ├── models.py               # SQLAlchemy table models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── crud.py                 # Database logic & business calculations
│   ├── ai_helper.py             # AI text-generation helpers
│   ├── copilot.py              # Retailer Copilot (AI function-calling agent)
│   ├── tool.py                 # Copilot tool definitions
│   └── config.py               # Environment variable loading
│
├── frontend/                   # Streamlit UI
│   ├── Home.py
│   └── pages/
│       ├── 1_Upload_Invoice.py
│       ├── 2_Customer_Profile.py
│       ├── 3_Prediction_And_Action.py
│       ├── 4_Business_Dashboard.py
│       ├── 5_Copilot.py
│       ├── 6_Credit_Overview.py
│       ├── 7_Product_Bundles.py
│       └── 8_Inventory_Signals.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Database Schema

Four core tables, normalized and linked by foreign keys:

- **customers** — identity + retailer-provided behavior profile (customer type, bargaining tendency, payment mode, preference tier, buying behavior)
- **invoices** — one row per invoice, linked to a customer
- **products** — master product catalog
- **invoice_items** — line items linking invoices to products (composite primary key)

```
customers ──< invoices ──< invoice_items >── products
  (1:many)      (1:many)                       (1:many)
```

---

## Setup & Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL
- A Groq API key ([console.groq.com](https://console.groq.com))

### 1. Clone and install dependencies
```bash
git clone <your-repo-url>
cd RETAILMIND_AI
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file inside `app/`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
GROQ_API_KEY=your_groq_api_key
GROQ_VISION_MODEL=qwen/qwen3.8-27b
```

### 3. Set up the database
Run the table creation SQL (see `models.py` for schema) against your PostgreSQL instance.

### 4. Run the backend
```bash
cd app
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000` — interactive API docs at `/docs`.

### 5. Run the frontend
In a separate terminal:
```bash
streamlit run frontend/Home.py
```
Frontend runs at `http://localhost:8501`.

---

## API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/upload-invoice` | POST | Upload an invoice image; extracts, validates, and saves it |
| `/update-customer-profile` | POST | Save a new customer's 5-question behavior profile |
| `/customer/{id}` | GET | Full customer intelligence profile |
| `/customer/{id}/prediction` | GET | Next-purchase prediction |
| `/customer/{id}/next-best-action` | GET | Recommended action + WhatsApp message |
| `/dashboard` | GET | Store-wide business summary + hero/weak products |
| `/credit-overview` | GET | Outstanding credit across all customers |
| `/product-bundles` | GET | Frequently co-purchased product pairs |
| `/inventory-signals` | GET | Fastest-moving products (last 30 days) |
| `/copilot` | POST | Natural-language business Q&A (AI agent with tool-calling) |

---

## Target Market

Small and medium grocery/kirana retailers in India — non-technical users who want business intelligence without complicated software or manual data entry. The architecture is designed to generalize to other retail categories in future versions.

---

## What Makes This Different

Not "ChatGPT for retailers." RetailMind is:
1. **Zero manual entry** — scan an invoice, that's it
2. **Persistent customer memory** — the system remembers behavior over time
3. **Time-aware intelligence** — learns real purchase intervals
4. **Action-oriented** — doesn't stop at analytics, recommends and drafts real actions
5. **Transaction-grounded** — every AI-generated answer is backed by real calculated data, never invented

---

## Team / Author

Built by Vaibhav for the AI Builders Hackathon 2026.