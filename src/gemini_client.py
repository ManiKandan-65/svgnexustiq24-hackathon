import os
import json
import urllib.request
import urllib.error
import traceback
from src.prompts import SYSTEM_PROMPT, build_copilot_prompt


def generate_deterministic_fallback(question, evidence_dict):
    """
    Generates a structured, evidence-grounded response directly from Python calculations.
    Ensures ZERO unrelated default fallbacks (e.g. Wireless Mouse is NEVER returned unless relevant).
    """
    # 1. Handle Unanswerable Questions (Profit, 2030 forecast, Competitor data)
    if evidence_dict.get("unanswerable"):
        reason = evidence_dict.get("reason", "The requested metric is not included in the dataset.")
        return {
            "answer": f"I cannot answer this question because {reason}",
            "key_numbers": [{"label": "Status", "value": "Data Not Available"}],
            "evidence": "Dataset schema (stores.csv, products.csv, sales.csv, inventory.csv)",
            "recommendation": "Consult external financial records or incorporate margin/forecast parameters into the retail dataset.",
            "assumptions_limitations": "The current dataset only tracks historical 90-day sales, revenue, cost, selling price, and stock levels.",
            "is_fallback": True,
            "is_unanswerable": True
        }

    # 2. Handle Product / Category Search No Matches
    if evidence_dict.get("no_match"):
        reason = evidence_dict.get("reason", "I couldn't find a matching product or category in the available retail data.")
        return {
            "answer": reason,
            "key_numbers": [{"label": "Search Result", "value": "0 Matches Found"}],
            "evidence": "products.csv & inventory.csv catalogue search",
            "recommendation": "Try searching for available categories (e.g. 'show electronics', 'stationery', 'kitchen') or specific product names.",
            "assumptions_limitations": "Catalog search is restricted to the 40 products and 8 categories present in the dataset.",
            "is_fallback": True,
            "is_unanswerable": True
        }

    # 3. Handle Ambiguous / Unknown Questions
    if evidence_dict.get("unknown_question"):
        reason = evidence_dict.get("reason", "I don't have enough information to answer that from the available retail data.")
        avail = evidence_dict.get("available_info", "")
        return {
            "answer": f"{reason}\n\n{avail}",
            "key_numbers": [{"label": "Supported Topics", "value": "Stockouts, Overstock, Store Ranking, Product Lookup, Sales Trends"}],
            "evidence": "RetailMind Operational Analytics Engine",
            "recommendation": "Please select a suggested question chip or ask about specific stockout risks, overstocks, store performance, or product categories.",
            "assumptions_limitations": "Only queries relating to historical 90-day retail operations can be evaluated.",
            "is_fallback": True,
            "is_unanswerable": True
        }

    intent = evidence_dict.get("intent", "GENERAL")

    # 4. Handle Specific Product Drop (e.g. Bluetooth Speaker)
    if intent == "SPECIFIC_PRODUCT_DROP":
        pname = evidence_dict.get("product_name", "Product")
        prev_m = evidence_dict.get("previous_month_sales", 0)
        curr_m = evidence_dict.get("current_month_sales", 0)
        decline = evidence_dict.get("decline_pct", 0)
        cause_exp = evidence_dict.get("cause_explanation", "")

        return {
            "answer": f"Monthly sales for {pname} declined by {abs(decline)}% from {prev_m} units last month to {curr_m} units this month.\n\n{cause_exp}",
            "key_numbers": [
                {"label": "Product", "value": pname},
                {"label": "Previous Month Sales", "value": f"{prev_m} units"},
                {"label": "Current Month Sales", "value": f"{curr_m} units"},
                {"label": "Sales Decline", "value": f"{decline}%"}
            ],
            "evidence": f"sales.csv monthly aggregation for {pname}",
            "recommendation": "Inspect store shelf placement, stock availability, pricing, and local competitor factors.",
            "assumptions_limitations": "The available dataset confirms the decline but does not contain promotion, pricing, or marketing records, so the root cause cannot be established from this dataset.",
            "is_fallback": True
        }

    # 5. Handle Product / Category Lookup (e.g. "computers", "laptop", "show electronics")
    if intent == "PRODUCT_LOOKUP":
        matched = evidence_dict.get("matched_products", [])
        title = evidence_dict.get("title", "Product Catalogue Search")
        
        lines = [f"{title}: Found {len(matched)} matching item(s) in retail inventory:\n"]
        key_nums = []
        for p in matched:
            cov = f"{p['days_remaining']} days" if p['days_remaining'] is not None else "Infinite"
            lines.append(f"• {p['product_name']} ({p['category']}) @ {p['store_name']}: Stock = {p['current_stock']} units | Avg Sales = {p['avg_daily_sales']}/day | Coverage = {cov} | Risk = {p['risk_level']}")
            key_nums.append({"label": p["product_name"], "value": f"Stock: {p['current_stock']} | Sales: {p['avg_daily_sales']}/d"})

        return {
            "answer": "\n".join(lines),
            "key_numbers": key_nums[:6],
            "evidence": f"products.csv and inventory.csv matching query tokens",
            "recommendation": "Review stock levels and daily sales velocity for matching catalogue items.",
            "assumptions_limitations": "Calculations based on 30-day average daily sales velocity.",
            "is_fallback": True
        }

    # 6. Handle Store Performance Ranking
    if intent == "STORE_PERFORMANCE":
        top = evidence_dict.get("top_store", {})
        all_s = evidence_dict.get("all_stores", [])
        top_name = top.get("store_name", "Store")
        top_rev = top.get("revenue", 0.0)

        lines = [f"The best performing store is {top_name} with Total Revenue of ₹{top_rev:,.2f}.\n\nFull Store Performance Ranking:"]
        key_nums = []
        for s in all_s:
            lines.append(f"• {s['store_name']} ({s['city']}): Revenue = ₹{s['revenue']:,.2f} | Units Sold = {s['units_sold']} | Growth = {s['sales_growth_pct']}% | Low Stock Items = {s['low_stock_count']}")
            key_nums.append({"label": s["store_name"], "value": f"₹{s['revenue']:,.2f}"})

        return {
            "answer": "\n".join(lines),
            "key_numbers": key_nums,
            "evidence": "sales.csv aggregated by store across 90 days",
            "recommendation": f"Maintain strong inventory support at top-performing {top_name} and address low stock items.",
            "assumptions_limitations": "Rankings based on 90-day cumulative sales revenue.",
            "is_fallback": True
        }

    # 7. Handle Alert Lists (Stockouts, Overstocks, Spikes, Drops, Attention)
    alerts = evidence_dict.get("alerts", [])
    if alerts:
        title = evidence_dict.get("title", "Retail Alerts")
        lines = [f"{title} (Found {len(alerts)} items):\n"]
        key_nums = []

        for a in alerts[:5]:
            lines.append(f"• {a['product_name']} @ {a['store_name']}: {a['alert_type']} ({a['metric_value']}). Action: {a['recommended_action']}")
            key_nums.append({"label": f"{a['product_name']} ({a['store_name']})", "value": a["metric_value"]})

        top = alerts[0]
        return {
            "answer": "\n".join(lines),
            "key_numbers": key_nums,
            "evidence": top["evidence_summary"],
            "recommendation": top["recommended_action"],
            "assumptions_limitations": "Assumes recent 30-day average daily sales velocity continues unchanged.",
            "is_fallback": True
        }

    # 8. General Sales Performance Summary
    rev = evidence_dict.get("total_revenue", 0.0)
    units = evidence_dict.get("units_sold", 0)
    return {
        "answer": f"Retail Operations Overview:\nTotal Revenue across all stores is ₹{rev:,.2f} over {units} total units sold.",
        "key_numbers": [
            {"label": "Total Revenue", "value": f"₹{rev:,.2f}"},
            {"label": "Units Sold", "value": f"{units} units"}
        ],
        "evidence": "sales.csv aggregated across 90 days",
        "recommendation": "Monitor high-risk stockout alerts and store performance rankings.",
        "assumptions_limitations": "Historical summary based on 90-day sales records.",
        "is_fallback": True
    }


def call_gemini_api(prompt_text):
    """
    Direct HTTPS REST API call to Gemini using urllib.request.
    Reads GEMINI_API_KEY from environment.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    # Try gemini-1.5-flash, gemini-2.0-flash, gemini-1.5-pro
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro"
    ]

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt_text}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    resp_body = json.loads(response.read().decode("utf-8"))
                    candidates = resp_body.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
        except Exception as err:
            print(f"[GeminiClient] Error calling {model_name}: {err}")

    return None


def parse_gemini_structured_response(text):
    """Parses Gemini's text response into structured fields."""
    if not text:
        return None

    sections = {
        "answer": "",
        "key_numbers": [],
        "evidence": "",
        "recommendation": "",
        "assumptions_limitations": ""
    }

    current_sec = "answer"
    lines = text.split("\n")

    for line in lines:
        upper = line.upper().strip()
        if upper.startswith("ANSWER:"):
            current_sec = "answer"
            sections["answer"] += line.split(":", 1)[1].strip() + "\n"
        elif upper.startswith("KEY NUMBERS:") or upper.startswith("KEY NUMBERS"):
            current_sec = "key_numbers"
        elif upper.startswith("EVIDENCE:") or upper.startswith("EVIDENCE"):
            current_sec = "evidence"
            val = line.split(":", 1)[1].strip() if ":" in line else ""
            if val:
                sections["evidence"] += val + "\n"
        elif upper.startswith("RECOMMENDATION:") or upper.startswith("RECOMMENDATION"):
            current_sec = "recommendation"
            val = line.split(":", 1)[1].strip() if ":" in line else ""
            if val:
                sections["recommendation"] += val + "\n"
        elif upper.startswith("ASSUMPTIONS") or upper.startswith("LIMITATIONS"):
            current_sec = "assumptions_limitations"
            val = line.split(":", 1)[1].strip() if ":" in line else ""
            if val:
                sections["assumptions_limitations"] += val + "\n"
        else:
            if current_sec == "key_numbers":
                cleaned = line.strip(" *-•")
                if cleaned:
                    if ":" in cleaned:
                        parts = cleaned.split(":", 1)
                        sections["key_numbers"].append({"label": parts[0].strip(), "value": parts[1].strip()})
                    else:
                        sections["key_numbers"].append({"label": "Metric", "value": cleaned})
            else:
                sections[current_sec] += line + "\n"

    sections["answer"] = sections["answer"].strip()
    sections["evidence"] = sections["evidence"].strip()
    sections["recommendation"] = sections["recommendation"].strip()
    sections["assumptions_limitations"] = sections["assumptions_limitations"].strip()

    if not sections["answer"]:
        sections["answer"] = text

    return sections


def query_copilot(question, evidence_dict, policy_context):
    """
    Primary Copilot Entry Point.
    Checks query relevance, executes Gemini API if available, or returns deterministic response.
    """
    # 1. Check if unanswerable, no_match, or unknown question
    if evidence_dict.get("unanswerable") or evidence_dict.get("no_match") or evidence_dict.get("unknown_question"):
        return generate_deterministic_fallback(question, evidence_dict)

    evidence_str = json.dumps(evidence_dict, indent=2)
    prompt = build_copilot_prompt(question, evidence_str, policy_context)

    raw_ai = call_gemini_api(prompt)
    if raw_ai:
        parsed = parse_gemini_structured_response(raw_ai)
        if parsed:
            parsed["is_fallback"] = False
            return parsed

    # Fallback to deterministic Python response
    return generate_deterministic_fallback(question, evidence_dict)
