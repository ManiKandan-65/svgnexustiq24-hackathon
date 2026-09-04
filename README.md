TRACK_ID=PS03
# RetailMind — Evidence-Grounded Sales & Inventory Copilot

RetailMind is an evidence-grounded AI copilot built for store managers running small retail operations. It separates **deterministic Python analytics** from **LLM reasoning** to eliminate numerical hallucinations, ensure data grounding, and present verifiable evidence trails for every operational recommendation.

## Problem Solved
Store managers often struggle to synthesize complex, multi-store inventory and sales records into immediate actionable decisions. AI LLMs when tasked with numerical analysis often invent numbers or hallucinate causes. RetailMind solves this by:
1. Performing 100% of mathematical and inventory risk calculations deterministically in Python.
2. Retrieving relevant local store management policies.
3. Supplying Gemini with calculated evidence to format concise, structured explanations adhering to a 5-part response structure (ANSWER, KEY NUMBERS, EVIDENCE, RECOMMENDATION, ASSUMPTIONS/LIMITATIONS).
4. Strictly refusing to guess when data is missing ("I Don't Know" protocol).

---

## Architectural Separation & Engineering Principles

```
  Human Manager Decision
            ▲
            │
┌───────────────────────┐
│  Structured Response  │ (ANSWER, NUMBERS, EVIDENCE, RECOMMENDATION, ASSUMPTIONS)
└───────────────────────┘
            ▲
            │
┌───────────────────────┐
│ Gemini REST Reasoning │ (urllib.request HTTPS call to Gemini API)
└───────────────────────┘
            ▲
            │
┌───────────────────────┐
│ Evidence & RAG Policy │ (Local policy chunks & keyword retrieval)
└───────────────────────┘
            ▲
            │
┌───────────────────────┐
│ Deterministic Engine  │ (Days of supply, sales growth %, spike & drop detection)
└───────────────────────┘
            ▲
            │
┌───────────────────────┐
│ Standard CSV Dataset  │ (stores.csv, products.csv, inventory.csv, sales.csv)
└───────────────────────┘
```

---

## Technology Stack (Zero External Python Package Architecture)

- **Backend**: Python 3.11 / 3.12 Standard Library (`http.server`, `urllib.request`, `json`, `csv`, `math`, `datetime`, `re`)
- **Frontend**: HTML5, Vanilla CSS3 (custom theme), Vanilla JavaScript (Web APIs, No React, No Tailwind build)
- **Data Persistence**: In-memory loaded CSV datasets (`stores.csv`, `products.csv`, `inventory.csv`, `sales.csv`)
- **AI Integration**: Gemini REST API (`gemini-2.5-flash` / `gemini-1.5-flash` via `urllib.request`)
- **Visualizations**: Pure SVG 90-Day Daily Sales Trend Engine

---

## Key Features

1. **Deterministic Analytics Engine**:
   - **Total Revenue & Unit Volume** aggregation across 90 days.
   - **Average Daily Sales (30d velocity)** calculation.
   - **Stock Coverage / Days Remaining** (`current_stock / average_daily_sales`).
   - **Stock-Out Risk Detection**: HIGH (&le; 7 days), MEDIUM (&le; 14 days).
   - **Overstock Detection**: Coverage &ge; 90 days or stock &ge; 3.5x reorder level.
   - **Sales Spike Detection**: &ge; 80% surge comparing recent 14d vs prior 14d.
   - **Sales Drop Detection**: &ge; 40% decline comparing current vs previous monthly sales.
   - **Store Performance Benchmark**: Revenue and volume ranking across stores.

2. **Evidence-Grounded Manager Copilot**:
   - Responds to natural language queries.
   - Outputs strict 5-part structured responses:
     - **ANSWER**: Direct explanation.
     - **KEY NUMBERS**: Bulleted deterministic metrics.
     - **EVIDENCE**: Exact data source and calculation formula.
     - **RECOMMENDATION**: Actionable manager recommendation.
     - **ASSUMPTIONS & LIMITATIONS**: Underlaying assumptions and data constraints.

3. **Strict "I Don't Know" & Data Limitation Protocol**:
   - Refuses to speculate on profit/margin when cost data is absent.
   - Explains that future multi-year 2030 forecasts are unanswerable with historical 90-day data.
   - States explicitly when sales drops cannot be attributed to a root cause due to missing promotional/pricing records.

4. **Robust Graceful Fallback**:
   - If `GEMINI_API_KEY` is missing or API request times out/fails, the backend seamlessly formats Python-calculated results into the structured 5-part output without crashing.

---

## Dataset Structure

The application automatically generates a synthetic 90-day retail dataset on first run:
- **`data/stores.csv`**: 3 store locations (`ST01`: Chennai Central, `ST02`: Coimbatore Main, `ST03`: Madurai Plaza).
- **`data/products.csv`**: 40 products across 8 categories (Electronics, Accessories, Home, Kitchen, Personal Care, Stationery, Grocery, Lifestyle).
- **`data/inventory.csv`**: Stock level, reorder level, unit cost, and selling price for each store/product pair (120 records).
- **`data/sales.csv`**: 90-day daily sales history (10,800 records).

---

## Knowledge Documents

- **`knowledge/inventory_policy.txt`**: Stockout risk thresholds, overstock definitions, lead time assumptions, and reorder guidelines.
- **`knowledge/retail_guidelines.txt`**: Guidelines for sales trend analysis, cause restriction rules for sales drops, and uncertainty handling.

---

## Setup & Running Instructions

### 1. Environment Variable (Optional for AI REST API)
Set your Gemini API key in your terminal session:
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
```
*(If unset, the application runs normally using the Deterministic Python Fallback Engine).*

### 2. Start Application
No `pip install` required! Run using Python standard library:
```cmd
python app.py
```
*(Or point to your installed Python binary, e.g. `py -3 app.py`)*

### 3. Open Dashboard
Open your browser and navigate to:
[http://localhost:8000](http://localhost:8000)

---

## Demo Test Scenarios

### DEMO 1 — Normal Case (Stock-Out Risk)
- **Question**: `"What products are running out?"`
- **Expected Result**: Lists products with low days remaining (e.g. Wireless Mouse at Chennai Central with 12 units in stock, 5.2/day sales, ~2.3 days remaining, HIGH risk badge, and "Reorder immediately" recommendation).

### DEMO 2 — Difficult Case (Unexplained Sales Drop)
- **Question**: `"Why did Bluetooth Speaker sales drop?"`
- **Expected Result**: Shows monthly sales drop (-90.0% decline from 20/day to 2/day), then states: `"The available dataset confirms a decline of 90.0%, but does not contain promotion, pricing, or marketing records, so the exact root cause cannot be established from this dataset."`

### DEMO 3 — Data Not Available ("I Don't Know" Protocol)
- **Question**: `"Which product has the highest profit?"`
- **Expected Result**: System responds: `"I cannot answer this question because profit or margin data is not present in the current dataset context."`

---

## Known Limitations

1. **Single-Node In-Memory Storage**: CSV files are cached in memory on startup. Real-time external database connectors can be integrated via `src/data_loader.py`.
2. **Standard Library Keyword Retrieval**: Uses token-overlap keyword scoring over local policy chunks. Can be augmented with embedding vector similarity when connected to an embedding API.
