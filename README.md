TRACK_ID=PS03
# NEXUS RETAIL COMMAND CENTER
### Real-Time Inventory Intelligence, Deterministic Analytics & Evidence-Grounded Decisions

NEXUS Retail Command Center is an enterprise-grade retail inventory intelligence platform designed for store managers and operations teams. Built around a **zero-hallucination architecture**, NEXUS strictly separates 100% deterministic Python calculations from natural-language AI reasoning. Every stock alert, demand forecast, reorder recommendation, and inter-store transfer is backed by an audit-ready mathematical breakdown.

---

## 🎯 Problem Statement

Running multi-store retail operations presents critical inventory challenges:

1. **Stockout Risks & Lost Revenue**: Store managers often miss impending stockouts until shelves are empty, leading to frustrated customers and lost sales.
2. **Overstock Capital Lockup**: Excess inventory ties up working capital in slow-moving items, increasing storage costs and markdown risks.
3. **Inefficient Inter-Store Stock Balancing**: While Store A experiences a critical stockout, Store B may hold excess inventory of the exact same product, but managers lack visibility to transfer stock.
4. **AI Hallucinations & Black-Box Decisions**: Generic AI chatbots often invent fake numbers or hallucinate arbitrary reasons for sales fluctuations without data backing.

---

## 💡 Solution

NEXUS Retail Command Center solves these problems through an integrated, evidence-grounded intelligence platform:

- **Deterministic Inventory Engine**: 100% reproducible Python calculations for stock coverage, daily sales velocity, and risk thresholds.
- **Demand Forecasting**: Deterministic 7-day and 14-day demand projections and estimated stockout dates.
- **Recommended Replenishment**: Automated target stock calculations ($\text{Avg Daily Sales} \times 14\text{d}$) and reorder quantity recommendations.
- **Smart Transfer Network**: Automated detection of inter-store stock balancing opportunities (transferring surplus stock from Store B to fulfill stockout risks at Store A).
- **What-If Inventory Simulator**: A non-mutating operational sandbox allowing managers to simulate demand shifts (-50% to +100%) and incoming stock before taking real-world action.
- **Explainable "WHY?" Decision Panels**: Audit-ready mathematical breakdowns for every recommendation.
- **Evidence Copilot**: Grounded natural-language query interface powered by Gemini 1.5 Flash + verified Python facts.

---

## ✨ Key Features

### 1. Command Center Overview Dashboard
- High-impact KPI Cards: `TOTAL PRODUCTS` (120), `CRITICAL STOCK` (44), `AT-RISK PRODUCTS` (44), `STABLE PRODUCTS`, and `ESTIMATED COVERAGE` (19.5d).
- **Inventory Health Matrix**: Multi-store grid displaying real-time store x product health status (`CRITICAL`, `WARNING`, `HEALTHY`).
- Store Performance Ranking table by revenue, volume, growth %, and low stock counts.

### 2. Inventory Catalogue
- Searchable catalog across 40 products and 8 categories.
- Filtering by risk status (`CRITICAL`, `WARNING`, `OVERSTOCK`, `HEALTHY`).
- Direct access to Product Details Side Drawer.

### 3. Smart Stock Alerts & Explainable "WHY?" Decision Panels
- Automatically sorted by operational urgency.
- Every alert contains a **"WHY?"** button opening an audit-ready mathematical breakdown showing the exact formulas and threshold comparisons used.

### 4. 7-Day / 14-Day Demand Forecast
- Deterministic demand forecasting based on 30-day sales velocity.
- Projected stock after 7 and 14 days.
- Estimated stockout dates ($ \text{latest\_date} + \lceil \text{coverage\_days} \rceil $).

### 5. Recommended Replenishment Engine
- Calculates Target Stock and Recommended Reorder Quantity.
- Urgency timeline badges (`Replenish within 24 hours` vs `Schedule within 48 hours`).

### 6. Smart Inter-Store Transfers
- Detects stockout risks at Store A ($\le 14$d coverage) alongside surplus inventory at Store B ($> 20$d coverage).
- Calculates safe transfer quantities and provides clear operational rationale.

### 7. What-If Inventory Simulator ("INVENTORY WHAT-IF LAB")
- Non-mutating interactive simulation sandbox.
- Controls for Daily Sales Velocity Change (-50% to +100%), Emergency Incoming Stock, and Target Coverage Days.
- Live recalculation of projected coverage, stockout dates, and delta reorder needs.

### 8. Product Details Side Drawer
- Slide-out drawer with 90-day daily sales **SVG Trend Chart**.
- 7d/14d demand forecast, reorder recommendations, and transfer opportunities.

### 9. Evidence Copilot & RAG Retrieval
- Grounded query engine for queries like *"Which products are at risk?"* or *"Where should stock be transferred?"*.
- Output structured into: `QUERY` $\rightarrow$ `ANSWER` $\rightarrow$ `CALCULATIONS` $\rightarrow$ `EVIDENCE USED` $\rightarrow$ `DECISION` $\rightarrow$ `ASSUMPTIONS`.

---

## 📐 How the Intelligence Works (Deterministic Formulas)

All numerical calculations are executed deterministically by Python standard library modules:

1. **Average Daily Sales Velocity (30d)**:
   $$\text{Avg Daily Sales} = \frac{\sum_{i=1}^{30} \text{Quantity Sold}_i}{30}$$

2. **Stock Coverage Days**:
   $$\text{Coverage Days} = \frac{\text{Current Stock}}{\text{Average Daily Sales}}$$

3. **Demand Forecast (7-Day & 14-Day)**:
   $$\text{Demand}_{7\text{d}} = \text{Avg Daily Sales} \times 7 \quad \mid \quad \text{Demand}_{14\text{d}} = \text{Avg Daily Sales} \times 14$$

4. **Target Stock**:
   $$\text{Target Stock} = \text{Avg Daily Sales} \times \text{Target Coverage Days (Default 14)}$$

5. **Recommended Reorder Quantity**:
   $$\text{Recommended Reorder} = \max(0, \text{Target Stock} - \text{Current Stock})$$

6. **Estimated Stockout Date**:
   $$\text{Stockout Date} = \text{Current Date} + \lceil \text{Coverage Days} \rceil \text{ days}$$

7. **Smart Transfer Logic**:
   $$\text{Transfer Qty} = \max\Big(5, \min\big(\text{Stock}_B - \text{ReorderLevel}_B, \, (14 - \text{Coverage}_A) \times \text{AvgSales}_A\big)\Big)$$
   *(Triggers when Store A Coverage $\le 14$d and Store B Coverage $\ge 20$d).*

---

## 💻 Technology Stack

NEXUS is engineered as a **ZERO-EXTERNAL-PYTHON-PACKAGE** application for maximum portability and fast startup:

- **Backend**: Python 3.11 / 3.12 Standard Library (`http.server`, `urllib.request`, `json`, `csv`, `math`, `datetime`, `re`)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Nexus Midnight/Cyan Dark Theme), Vanilla JavaScript (Web APIs, No React, No Tailwind build)
- **Data Persistence**: In-memory loaded CSV datasets (`stores.csv`, `products.csv`, `inventory.csv`, `sales.csv`)
- **AI Integration**: Gemini REST API (`gemini-1.5-flash` / `gemini-2.0-flash` via standard `urllib.request`)
- **Data Visualizations**: Pure SVG 90-Day Daily Sales Trend Engine

---

## 🏗️ System Architecture

```
User Query / UI Interaction
            │
            ▼
   Nexus Web Dashboard (HTML5 / Vanilla CSS3 / Vanilla JS)
            │
            ▼
   Python HTTP Server (http.server.HTTPServer on port 8000)
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│             DETERMINISTIC ANALYTICS ENGINE                  │
│  - Stock Coverage & Daily Sales Velocity Calculation        │
│  - 7d/14d Demand Forecasting & Stockout Date Projection     │
│  - Target Stock & Replenishment Reorder Engine              │
│  - Smart Inter-Store Transfer Network Logic                 │
│  - Inventory What-If Simulation Sandbox                     │
└─────────────────────────────────────────────────────────────┘
            │                                  │
            ▼                                  ▼
 Local Inventory & Policy Data       Gemini REST API (urllib.request)
 (stores, products, sales, policy)   (Natural-Language Explanation)
            │                                  │
            └──────────────────┬───────────────┘
                               │
                               ▼
            Explainable & Grounded Decision Panel
```

---

## 📊 Example Decision

### Case Study: Wireless Mouse @ Chennai Central

- **Current Stock**: 12 units
- **Average Daily Sales**: 5.3 units/day
- **Calculated Coverage**: 2.3 days
- **Critical Threshold**: 7.0 days
- **Target Stock (14d)**: 74 units
- **Recommended Reorder**: 62 units

#### Decision Explanation:
> Current inventory of 12 units divided by recent average daily sales of 5.3 units/day yields approximately 2.3 days of supply. Because 2.3 days is below the critical safe threshold of 7.0 days, the deterministic engine flags this SKU as **CRITICAL STOCK-OUT RISK** and issues a recommendation: **REORDER 62 UNITS IMMEDIATELY**.
> 
> Simultaneously, the **Smart Transfer Network** detects that Coimbatore Main holds 91 units (20.4 days coverage) of Wireless Mouse and recommends an immediate inter-store transfer of **61 units** to bridge the gap.

---

## 🔬 What-If Simulator ("INVENTORY WHAT-IF LAB")

The What-If Simulator provides a non-mutating operational sandbox allowing store managers to evaluate hypothetical scenarios:
- **Daily Sales Velocity Change**: Adjust slider from -50% to +100% demand shift.
- **Incoming Emergency Stock**: Test adding 10, 25, 50+ emergency units.
- **Target Coverage Days**: Modify replenishment buffer targets (default 14 days).

All simulated outputs (projected coverage, stockout date, risk status, additional reorder needed) are calculated dynamically without modifying the underlying CSV database.

---

## ✅ Verification & Testing Results

The complete NEXUS Retail Command Center test suite was executed and verified:

```text
=== TESTING NEXUS COMMAND CENTER ENDPOINTS ===
Total Products: 120, Critical Stock: 44, At-Risk: 44, Coverage: 19.5d
Health Matrix Rows: 40
Sample Matrix Item: Wireless Mouse -> Chennai Central: CRITICAL (2.3d)

Demand Forecasts Count: 120
Sample Forecast: Wireless Mouse @ Chennai Central -> 7d Demand: 37.1 units, Stockout Date: Sep 07, 2026

Reorders Count: 44
Sample Reorder: Wireless Mouse @ Chennai Central -> Current: 12, Recommended Reorder: 62 units

Smart Transfers Count: 4
Sample Transfer: Move 61 units of Wireless Mouse from Coimbatore Main to Chennai Central

Simulation Result: Wireless Mouse @ Chennai Central (+20% Sales, +25 Stock) -> Simulated Coverage: 5.8 days, Risk: CRITICAL STOCK-OUT RISK

=== ALL NEXUS COMMAND CENTER ENDPOINTS VERIFIED 100% ===
```

---

## 🚀 How to Run Locally

### 1. Environment Variable (Optional for Gemini REST API)
Set your Gemini API key in your terminal:
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```
*(If unset, NEXUS automatically operates using the Deterministic Python Fallback Engine).*

### 2. Start Application
No `pip install` or `npm install` required! Run using Python standard library:
```cmd
python app.py
```

### 3. Access Command Center
Open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

---

## ⚡ Hackathon Value & Operational Impact

1. **Zero Hallucination Risk**: Prevents costly retail ordering mistakes caused by black-box AI hallucinations.
2. **Actionable Financial Savings**: Identifies inter-store transfer opportunities before placing expensive new purchase orders.
3. **Instant Transparency**: "WHY?" buttons build immediate trust with retail store managers.
4. **Zero-Dependency Portability**: Boots up in milliseconds on any Python 3.11+ environment without dependency conflicts.

---

## 🔮 Future Enhancements

- **Real-Time POS Streaming**: Integration with live Point-of-Sale transaction streams via WebSockets.
- **Automated Purchase Order Generation**: One-click PDF/EDI purchase order creation for suppliers.
- **Machine Learning Seasonal Forecasting**: Advanced ARIMA/Prophet models for seasonal demand peaks.
- **Multi-Tenant Role Access**: Dedicated views for Store Managers, Regional Supervisors, and Procurement Directors.
- **Cloud Container Deployment**: Dockerized container deployment to AWS/GCP serverless environments.

---

## 📁 Project Structure

```text
Retail mind/
│
├── app.py                      # Main HTTP server & API route handler
├── README.md                   # Project documentation (TRACK_ID=PS03)
├── requirements.txt            # Zero-dependency specification file
├── .gitignore                  # Git exclusion rules
│
├── src/                        # Core Python Modules (Standard Library)
│   ├── __init__.py
│   ├── analytics.py            # Deterministic engine, formulas, forecasts & transfers
│   ├── data_loader.py          # Synthetic dataset generator & CSV reader
│   ├── gemini_client.py        # Gemini REST API client with deterministic fallback
│   ├── retrieval.py            # Local RAG keyword retrieval engine
│   ├── prompts.py              # Grounded system prompts & structured templates
│   └── models.py               # Data models & dataclass structures
│
├── data/                       # CSV Datasets
│   ├── stores.csv              # 3 retail stores (Chennai, Coimbatore, Madurai)
│   ├── products.csv            # 40 products across 8 categories
│   ├── inventory.csv           # Stock levels, unit costs, selling prices
│   └── sales.csv               # 90-day daily sales history (10,800 records)
│
├── knowledge/                  # Local Knowledge Base Chunks
│   ├── inventory_policy.txt    # Risk thresholds & reorder rules
│   └── retail_guidelines.txt   # Trend analysis & uncertainty rules
│
├── static/                     # Web Assets
│   ├── style.css               # Nexus Midnight/Cyan Dark Theme
│   └── app.js                  # Navigation router, simulator & SVG chart engine
│
└── templates/                  # HTML Templates
    └── index.html              # Nexus Command Center Single-Page App
```

---

## 🔒 Security

All secrets, environment variables, credentials, and temporary cache files are strictly excluded from version control via `.gitignore`. The application never exposes API keys to client-side JavaScript.

---

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
