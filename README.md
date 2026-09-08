# RetailMind AI

### *From Data → Decisions → Actions*

An AI-powered business intelligence platform for small retailers that transforms raw invoices into persistent customer memory, anticipates repeat buying cycles, and recommends high-impact business actions — with zero manual data entry.

> **AI Builders Hackathon 2026 Submission**
> **Author:** Vaibhav
> **Status:** Live Full-Stack Application

---

## ⚡ The Quick Rundown

```mermaid
graph LR
    A[📄 Raw Invoice] --> B[👁️ Vision AI Extraction]
    B --> C[(🗄️ Scoped Database)]
    C --> D[📊 Deterministic Metrics]
    D --> E[🔮 Prediction Engine]
    E --> F[💬 Next Best Action / WhatsApp]

```

* **Core Innovation:** Transaction-grounded AI agent using tool calling over deterministic business logic. The AI never invents or guesses financial metrics.
* **Target Audience:** Indian kirana stores, independent grocers, and small retail operators who lack enterprise ERP tooling.

---

## 📌 The Problem vs. The Solution

| The Traditional Kirana Challenge | The RetailMind AI Solution |
| --- | --- |
| Customer data is trapped across handwritten slips and paper receipts. | **Zero Manual Entry:** Vision LLMs parse handwritten and printed bills into structured records instantly. |
| Shopkeepers cannot track who is due for refills or recurring orders. | **Interval Prediction:** Automatically models typical order cycles to flag overdue and due customers. |
| Outstanding credit (*udhaar*) is manually recorded in paper diaries. | **Credit Intelligence:** Centralizes and tracks unsettled balances on a per-customer basis. |
| Generic, detached analytics dashboards with no actionable output. | **Action-Driven Retention:** Generates contextual, ready-to-send WhatsApp messages tailored to purchase history. |

---

## 🛠️ Architecture & System Design

RetailMind separates non-deterministic AI generation from deterministic transactional math: **AI extracts and explains; the database calculates.**

```mermaid
flowchart TD
    subgraph Client Layer
        UI[Streamlit Cloud Frontend]
    end

    subgraph Authentication
        SupaAuth[Supabase Auth / Email OTP]
    end

    subgraph Application Layer [Render Cloud]
        API[FastAPI Gateway]
        Deps[Dependency Injection & Scoping]
        Tools[Deterministic BI Tools]
        Agent[Copilot Tool-Calling Agent]
    end

    subgraph Data & AI Infrastructure
        PG[(Neon PostgreSQL Multi-Tenant DB)]
        GroqVis[Groq: Qwen Vision Model]
        GroqText[Groq: GPT-OSS 120B]
    end

    UI -->|Bearer Token| API
    UI -.->|OTP Handshake| SupaAuth
    API --> Deps
    Deps -->|Validate User ID| SupaAuth
    API --> GroqVis
    API --> Tools
    Tools --> PG
    Agent <-->|Dynamic Function Calls| Tools
    Agent <-->|Context Grounding| GroqText

```

### Multi-Tenant Isolation

* Every incoming request validates a **Supabase Bearer Token** server-side against Supabase's `/auth/v1/user` endpoint — tokens are never trusted at face value.
* The backend resolves `supabase_user_id` → `business_id` internally; this mapping is never accepted from the client.
* The frontend cannot specify or override the target business tenant, strictly mitigating tenant crossover vulnerabilities.
* Database-level composite primary keys (`invoice_id + business_id`, `product_id + business_id`) prevent ID collisions between tenants at the schema level, not just the application level.

---

## 🔒 Security & Testing

Multi-tenant isolation was manually verified end-to-end, not just designed on paper:

* Two independent Supabase accounts were created and used to log into the live deployment.
* Each account uploaded separate invoices and generated separate customer/product records.
* Verified directly in the production database that each account's queries (dashboard, customer profiles, copilot, credit overview) return **only** their own business's data — no cross-tenant leakage.
* The AI copilot's tool-calling layer explicitly strips any `business_id` argument the LLM attempts to supply and replaces it with the authenticated user's real, server-derived business_id before every database call.

---

## 🚀 Key Features

* **Intelligent Invoice Ingestion:** Vision-driven extraction for products, units, price tiers, and buyer details from camera captures or scans.
* **Customer Behavioral Profiling:** A concise 5-question qualitative profile (bargaining style, preference tier, payment mode) added for newly detected customers to supplement transaction data.
* **Cadence Engine (Next-Purchase Timing):** Tracks variance in purchase dates to classify buyers as *Not Due Yet*, *Approaching*, or *Overdue*.
* **Next Best Action Generator:** Turns stale accounts into targeted customer retention by producing personalized WhatsApp drafts featuring their favorite products.
* **Store Health Indicators:** Real-time visibility into hero items, low-velocity products, transaction volumes, and 30-day demand signals.
* **Product Co-Occurrence Detection:** Native basket analysis identifying items frequently ordered together for bundle creation.
* **Natural Language Copilot:** An autonomous, read-only analytics agent equipped with tool-calling capabilities and conversation memory to query the store's PostgreSQL metrics securely.
* **Customer Search:** Retailers look customers up by name or phone — no need to remember internal database IDs.

---

## 🗄️ Database Schema Overview

```
                      +-------------------+
                      |    Businesses     |
                      +-------------------+
                      | business_id (PK)  |
                      | supabase_user_id  |
                      | business_name     |
                      +---------+---------+
                                |
        +-----------------------+-----------------------+
        | 1:N                                           | 1:N
+-------v---------+                             +-------v---------+
|    Customers    |                             |    Products     |
+-----------------+                             +-----------------+
| customer_id(PK) |                             | product_id (PK)*|
| business_id(FK) |                             | business_id(PK)*|
| name, phone     |                             | product_name    |
| behavioral_tags |                             +--------+--------+
+-------+---------+                                      |
        |                                                |
        | 1:N                                            | 1:N
+-------v---------+                             +--------v--------+
|    Invoices     | 1:N                         |  Invoice Items  |
+-----------------+---------------------------->+-----------------+
| invoice_id (PK)*|                             | invoice_id (PK) |
| business_id(PK)*|                             | product_id (PK) |
| customer_id(FK) |                             | business_id(FK) |
| totals & credit |                             | qty, unit_price |
+-----------------+                             +-----------------+

* Composite primary key (id + business_id) — allows two
  different businesses to safely use the same invoice/product IDs.
```

---

## 📡 Core API Specification

All endpoints below (except health checks) require a valid `Authorization: Bearer <supabase_access_token>` header.

| Endpoint | Method | Role | Payload / Returns |
| --- | --- | --- | --- |
| `/upload-invoice` | `POST` | Processes visual receipt | `multipart/form-data` → Extracted JSON |
| `/update-customer-profile` | `POST` | Enriches customer record | Behavioral questionnaire fields |
| `/customer-search` | `GET` | Directory lookup | Query param: `name` or `phone` |
| `/customer/{id}` | `GET` | Deep customer dossier | Lifetime metrics, favorite items, balance |
| `/customer/{id}/prediction` | `GET` | Replenishment forecaster | Purchase cadence classification |
| `/customer/{id}/next-best-action` | `GET` | Retention engine | Structured recommendations + WhatsApp text |
| `/dashboard` | `GET` | Aggregate performance | Sales totals, AOV, hero & weak items |
| `/credit-overview` | `GET` | Udhaar monitor | Ledger of outstanding balances |
| `/product-bundles` | `GET` | Affinity analysis | Top co-occurring product combinations |
| `/inventory-signals` | `GET` | Volume radar | 30-day velocity leaders |
| `/copilot` | `POST` | Plain-English interface | Tool-calling Q&A with conversational memory |

---

## 💻 Tech Stack Summary

```
Frontend            Streamlit Community Cloud
API Framework       FastAPI + Pydantic v2
Database            PostgreSQL (Hosted via Neon)
ORM                 SQLAlchemy
Auth Layer          Supabase Auth (Passwordless Email OTP, via direct HTTPX calls)
AI Inference        Groq LPU Acceleration
Vision Model        Qwen Vision
Language Model      GPT-OSS 120B (Tool Calling & Action Copy)
Deployment          Render (FastAPI) + Streamlit Cloud (UI)

```

---

## ⚙️ Local Development Setup

### 1. Clone & Set Up Virtual Environment

```bash
git clone <your-repo-url>
cd RETAILMIND_AI

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Configure Environment

Create `app/.env`:

```ini
DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
GROQ_API_KEY=your_groq_api_key
GROQ_VISION_MODEL=qwen/qwen3.8-27b
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_publishable_key

```

For the Streamlit frontend, also create `.streamlit/secrets.toml`:

```toml
[supabase]
url = "your_supabase_project_url"
key = "your_supabase_publishable_key"
```

### 4. Run Application Services

```bash
# Terminal 1: Backend API (from /app)
cd app
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend Dashboard (from project root)
streamlit run frontend/Home.py

```

* **Swagger Docs:** `http://127.0.0.1:8000/docs`
* **Streamlit UI:** `http://localhost:8501`

---

## 🗺️ Product Roadmap

* [ ] Live inventory tracking with automatic depletion alerts
* [ ] Automated WhatsApp Business Cloud API integration for 1-click broadcasts
* [ ] Predictive bulk replenishment alerts for store managers
* [ ] Batch legacy invoice scanning for historical record migration
* [ ] Offline-first mobile interface (PWA) tailored for counter registers
* [ ] Business-level sanity validation layer (reject/flag implausible extracted values before they reach the database)