import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from src.data_loader import load_dataset, validate_data_quality
from src.analytics import (
    calculate_total_revenue,
    calculate_units_sold,
    calculate_store_performance,
    calculate_product_performance,
    get_all_alerts,
    parse_question_intent,
    detect_stockout_risk,
    calculate_inventory_matrix,
    calculate_demand_forecast,
    calculate_smart_reorders,
    calculate_smart_transfers,
    run_inventory_simulation
)
from src.retrieval import retrieve_relevant_context
from src.gemini_client import query_copilot


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread for optimal UI responsiveness."""
    daemon_threads = True


class RetailMindRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP Request Handler serving Nexus Retail Command Center."""

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200, "text/plain")

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        store_id = query_params.get("store_id", [None])[0]
        if store_id == "ALL":
            store_id = None

        dataset = load_dataset()

        # 1. SERVE HTML TEMPLATE
        if path in ["/", "/index.html"]:
            html_path = os.path.join(ROOT_DIR, "templates", "index.html")
            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_headers(200, "text/html; charset=utf-8")
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self._set_headers(500, "text/plain")
                self.wfile.write(f"Error loading command center template: {e}".encode("utf-8"))
            return

        # 2. SERVE STATIC CSS & JS
        if path.startswith("/static/"):
            rel_path = path.lstrip("/")
            file_path = os.path.join(ROOT_DIR, rel_path)
            if os.path.exists(file_path):
                mime = "text/css" if file_path.endswith(".css") else "application/javascript"
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_headers(200, f"{mime}; charset=utf-8")
                self.wfile.write(content.encode("utf-8"))
                return
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"Static file not found.")
                return

        # 3. API ENDPOINTS
        if path == "/api/dashboard":
            total_rev = calculate_total_revenue(dataset["sales"], store_id=store_id)
            total_units = calculate_units_sold(dataset["sales"], store_id=store_id)
            stockouts_critical = detect_stockout_risk(dataset, store_id=store_id, high_threshold=7.0)
            stockouts_atrisk = detect_stockout_risk(dataset, store_id=store_id, high_threshold=7.0, med_threshold=14.0)
            all_alerts = get_all_alerts(dataset, store_id=store_id)
            warnings = validate_data_quality(dataset)

            # Compute stable count & coverage avg
            all_prods = calculate_product_performance(dataset, store_id=store_id)
            stable_count = sum(1 for p in all_prods if p["risk_level"] == "HEALTHY")
            valid_covs = [p["days_remaining"] for p in all_prods if p["days_remaining"] is not None and p["days_remaining"] < 365]
            avg_coverage = round(sum(valid_covs) / float(len(valid_covs)), 1) if valid_covs else 0.0

            payload = {
                "total_products": len(all_prods),
                "total_revenue": total_rev,
                "units_sold": total_units,
                "critical_stock_count": len(stockouts_critical),
                "at_risk_count": len(stockouts_atrisk),
                "stable_count": stable_count,
                "avg_coverage_days": avg_coverage,
                "attention_count": len(all_alerts),
                "alerts": all_alerts,
                "data_quality_warnings": warnings
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(payload).encode("utf-8"))
            return

        if path == "/api/matrix":
            matrix = calculate_inventory_matrix(dataset)
            self._set_headers(200)
            self.wfile.write(json.dumps(matrix).encode("utf-8"))
            return

        if path == "/api/forecast":
            forecasts = calculate_demand_forecast(dataset, store_id=store_id)
            self._set_headers(200)
            self.wfile.write(json.dumps(forecasts).encode("utf-8"))
            return

        if path == "/api/reorder":
            target_cov = int(query_params.get("target_coverage", [14])[0])
            reorders = calculate_smart_reorders(dataset, store_id=store_id, target_coverage=target_cov)
            self._set_headers(200)
            self.wfile.write(json.dumps(reorders).encode("utf-8"))
            return

        if path == "/api/transfers":
            transfers = calculate_smart_transfers(dataset)
            self._set_headers(200)
            self.wfile.write(json.dumps(transfers).encode("utf-8"))
            return

        if path == "/api/products":
            prods = calculate_product_performance(dataset, store_id=store_id)
            self._set_headers(200)
            self.wfile.write(json.dumps(prods).encode("utf-8"))
            return

        if path == "/api/stores":
            stores_perf = calculate_store_performance(dataset)
            self._set_headers(200)
            self.wfile.write(json.dumps(stores_perf).encode("utf-8"))
            return

        if path == "/api/alerts":
            all_alerts = get_all_alerts(dataset, store_id=store_id)
            self._set_headers(200)
            self.wfile.write(json.dumps(all_alerts).encode("utf-8"))
            return

        if path in ["/api/product", "/api/product/"]:
            prod_id = query_params.get("id", [None])[0] or query_params.get("product_id", [None])[0]
            if not prod_id:
                parts = [p for p in path.split("/") if p]
                if len(parts) >= 3:
                    prod_id = parts[2]

            if not prod_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing product id parameter"}).encode("utf-8"))
                return

            prods = calculate_product_performance(dataset, store_id=store_id)
            prod_info = next((p for p in prods if p["product_id"] == prod_id), None)

            if not prod_info:
                all_prods = calculate_product_performance(dataset, store_id=None)
                prod_info = next((p for p in all_prods if p["product_id"] == prod_id), None)

            if not prod_info:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Product {prod_id} not found"}).encode("utf-8"))
                return

            # Fetch daily sales trend (last 90 days)
            sales_history = []
            for s in dataset["sales"]:
                if s["product_id"] == prod_id and (store_id is None or s["store_id"] == store_id):
                    sales_history.append({"date": s["date"], "quantity_sold": s["quantity_sold"], "revenue": s["revenue"]})

            sales_history.sort(key=lambda x: x["date"])

            daily_map = {}
            for sh in sales_history:
                d = sh["date"]
                if d not in daily_map:
                    daily_map[d] = 0
                daily_map[d] += sh["quantity_sold"]

            trend = [{"date": k, "quantity_sold": v} for k, v in sorted(daily_map.items())]
            prod_info["sales_trend"] = trend

            # Add demand forecast and transfer opportunities for product drawer
            forecasts = calculate_demand_forecast(dataset, store_id=store_id)
            fc_item = next((f for f in forecasts if f["product_id"] == prod_id), None)
            prod_info["demand_forecast"] = fc_item

            transfers = calculate_smart_transfers(dataset)
            prod_transfers = [t for t in transfers if t["product_id"] == prod_id]
            prod_info["transfer_opportunities"] = prod_transfers

            self._set_headers(200)
            self.wfile.write(json.dumps(prod_info).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"Endpoint not found.")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/simulate":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(post_body)
            except Exception:
                data = {}

            store_id = data.get("store_id", "ST01")
            product_id = data.get("product_id", "PRD001")
            sales_change_pct = float(data.get("sales_change_pct", 0.0))
            incoming_stock = int(data.get("incoming_stock", 0))
            target_days = int(data.get("target_coverage_days", 14))

            dataset = load_dataset()
            sim_res = run_inventory_simulation(dataset, store_id, product_id, sales_change_pct, incoming_stock, target_days)

            self._set_headers(200)
            self.wfile.write(json.dumps(sim_res).encode("utf-8"))
            return

        if path == "/api/copilot":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(post_body)
            except Exception:
                data = {}

            question = data.get("question", "").strip()
            store_id = data.get("store_id", None)
            if store_id == "ALL":
                store_id = None

            if not question:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "answer": "Please enter a valid question for Nexus Copilot.",
                    "key_numbers": [],
                    "evidence": "N/A",
                    "recommendation": "Provide a query such as 'What products are running out?'.",
                    "assumptions_limitations": "Input was empty."
                }).encode("utf-8"))
                return

            dataset = load_dataset()

            # Step 1: Deterministic Analytics & Intent parsing
            evidence_dict = parse_question_intent(question, dataset)

            # Step 2: Local RAG Knowledge Retrieval
            policy_context = retrieve_relevant_context(question)

            # Step 3: Call Gemini REST API / Fallback
            response_payload = query_copilot(question, evidence_dict, policy_context)

            self._set_headers(200)
            self.wfile.write(json.dumps(response_payload).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"Endpoint not found.")


def run_server(port=8000):
    """Starts the Nexus Command Center pure Python HTTP server on port 8000."""
    server_address = ("", port)
    httpd = ThreadedHTTPServer(server_address, RetailMindRequestHandler)
    print(f"==================================================")
    print(f" NEXUS RETAIL COMMAND CENTER — ENGINE ACTIVE")
    print(f" Listening on http://localhost:{port}")
    print(f" Standard Library Only (Zero External Dependencies)")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down Nexus Command Center server...")
        httpd.server_close()


if __name__ == "__main__":
    load_dataset()
    run_server(port=8000)
