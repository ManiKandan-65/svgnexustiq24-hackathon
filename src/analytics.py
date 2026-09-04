import math
from datetime import datetime, timedelta

def get_latest_date(sales):
    """Finds the latest date in sales records."""
    if not sales:
        return datetime.now().strftime("%Y-%m-%d")
    return max(s["date"] for s in sales)


def filter_sales_by_date_range(sales, start_date_str, end_date_str, store_id=None, product_id=None):
    """Filters sales records within a date range and optional store/product filters."""
    result = []
    for s in sales:
        if store_id and s["store_id"] != store_id:
            continue
        if product_id and s["product_id"] != product_id:
            continue
        if start_date_str <= s["date"] <= end_date_str:
            result.append(s)
    return result


def calculate_total_revenue(sales, store_id=None):
    """Calculates total revenue across all sales or for a specific store."""
    total = 0.0
    for s in sales:
        if store_id and s["store_id"] != store_id:
            continue
        total += s["revenue"]
    return round(total, 2)


def calculate_units_sold(sales, store_id=None):
    """Calculates total units sold."""
    total = 0
    for s in sales:
        if store_id and s["store_id"] != store_id:
            continue
        total += s["quantity_sold"]
    return total


def calculate_average_daily_sales(sales, store_id=None, product_id=None, days=30):
    """Calculates average daily sales over the last N days."""
    latest_str = get_latest_date(sales)
    latest_dt = datetime.strptime(latest_str, "%Y-%m-%d")
    start_dt = latest_dt - timedelta(days=days - 1)
    start_str = start_dt.strftime("%Y-%m-%d")

    filtered = filter_sales_by_date_range(sales, start_str, latest_str, store_id, product_id)
    total_units = sum(s["quantity_sold"] for s in filtered)
    avg = total_units / float(days)
    return round(avg, 2)


def calculate_monthly_sales(sales, store_id=None, product_id=None):
    """Calculates units sold in the most recent 30-day period."""
    latest_str = get_latest_date(sales)
    latest_dt = datetime.strptime(latest_str, "%Y-%m-%d")
    start_dt = latest_dt - timedelta(days=29)
    start_str = start_dt.strftime("%Y-%m-%d")

    filtered = filter_sales_by_date_range(sales, start_str, latest_str, store_id, product_id)
    return sum(s["quantity_sold"] for s in filtered)


def calculate_previous_month_sales(sales, store_id=None, product_id=None):
    """Calculates units sold in the prior 30-day period (day 30 to day 59 back)."""
    latest_str = get_latest_date(sales)
    latest_dt = datetime.strptime(latest_str, "%Y-%m-%d")
    end_dt = latest_dt - timedelta(days=30)
    start_dt = latest_dt - timedelta(days=59)

    filtered = filter_sales_by_date_range(sales, start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"), store_id, product_id)
    return sum(s["quantity_sold"] for s in filtered)


def calculate_growth_percentage(current, previous):
    """Calculates growth percentage between previous and current values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    growth = ((current - previous) / float(previous)) * 100.0
    return round(growth, 1)


def calculate_days_remaining(current_stock, avg_daily_sales):
    """Calculates stock coverage / days remaining."""
    if avg_daily_sales <= 0:
        return None
    days = current_stock / float(avg_daily_sales)
    return round(days, 1)


def detect_stockout_risk(dataset, store_id=None, high_threshold=7.0, med_threshold=14.0):
    """Detects products at risk of running out of stock."""
    alerts = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s for s in dataset["stores"]}

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]
        stock = inv["current_stock"]

        avg_daily = calculate_average_daily_sales(dataset["sales"], store_id=sid, product_id=pid, days=30)
        days_left = calculate_days_remaining(stock, avg_daily)

        if days_left is not None and days_left <= med_threshold:
            risk_level = "CRITICAL STOCK-OUT RISK" if days_left <= high_threshold else "WARNING STOCK-OUT RISK"
            severity = "CRITICAL" if days_left <= high_threshold else "WARNING"

            prod = prod_map.get(pid, {"product_name": pid, "category": "General"})
            st = store_map.get(sid, {"store_name": sid})

            alerts.append({
                "alert_id": f"STOCKOUT_{sid}_{pid}",
                "alert_type": risk_level,
                "severity": severity,
                "product_id": pid,
                "product_name": prod["product_name"],
                "category": prod["category"],
                "store_id": sid,
                "store_name": st["store_name"],
                "current_stock": stock,
                "reorder_level": inv["reorder_level"],
                "avg_daily_sales": avg_daily,
                "days_remaining": days_left,
                "metric_value": f"{days_left} days remaining",
                "why_it_matters": f"Current stock of {stock} units will be depleted in approx {days_left} days based on recent sales velocity of {avg_daily} units/day.",
                "recommended_action": "REORDER IMMEDIATELY" if severity == "CRITICAL" else "SCHEDULE REPLENISHMENT WITHIN 48 HOURS",
                "evidence_summary": f"Inventory: {stock} units | 30d Avg Sales: {avg_daily}/day | Coverage: {days_left} days | Threshold: {high_threshold}d"
            })

    alerts.sort(key=lambda x: x["days_remaining"] if x["days_remaining"] is not None else 999)
    return alerts


def detect_overstock(dataset, store_id=None, days_threshold=90.0):
    """Detects overstocked products."""
    alerts = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s for s in dataset["stores"]}

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]
        stock = inv["current_stock"]

        avg_daily = calculate_average_daily_sales(dataset["sales"], store_id=sid, product_id=pid, days=30)
        days_left = calculate_days_remaining(stock, avg_daily)

        is_overstocked = False
        if days_left is not None and days_left >= days_threshold:
            is_overstocked = True
        elif avg_daily > 0 and stock >= (inv["reorder_level"] * 3.5):
            is_overstocked = True
        elif avg_daily == 0 and stock > 50:
            is_overstocked = True
            days_left = 999.0

        if is_overstocked:
            prod = prod_map.get(pid, {"product_name": pid, "category": "General"})
            st = store_map.get(sid, {"store_name": sid})
            days_str = f"{days_left} days" if days_left and days_left < 999 else "Infinite (Zero sales)"

            alerts.append({
                "alert_id": f"OVERSTOCK_{sid}_{pid}",
                "alert_type": "OVERSTOCK",
                "severity": "WARNING",
                "product_id": pid,
                "product_name": prod["product_name"],
                "category": prod["category"],
                "store_id": sid,
                "store_name": st["store_name"],
                "current_stock": stock,
                "reorder_level": inv["reorder_level"],
                "avg_daily_sales": avg_daily,
                "days_remaining": days_left,
                "metric_value": f"{days_str} stock coverage",
                "why_it_matters": f"Current inventory of {stock} units represents {days_str} of supply, tying up working capital.",
                "recommended_action": "REVIEW REPLENISHMENT & CONSIDER PROMOTION / TRANSFER",
                "evidence_summary": f"Inventory: {stock} units | 30d Avg Sales: {avg_daily}/day | Coverage: {days_str}"
            })

    return alerts


def detect_sales_spike(dataset, store_id=None):
    """Detects recent sales spikes (>80% surge comparing recent 14d vs prior 14d)."""
    alerts = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s for s in dataset["stores"]}
    latest_str = get_latest_date(dataset["sales"])
    latest_dt = datetime.strptime(latest_str, "%Y-%m-%d")

    r_start = (latest_dt - timedelta(days=13)).strftime("%Y-%m-%d")
    p_end = (latest_dt - timedelta(days=14)).strftime("%Y-%m-%d")
    p_start = (latest_dt - timedelta(days=27)).strftime("%Y-%m-%d")

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]

        r_sales = filter_sales_by_date_range(dataset["sales"], r_start, latest_str, sid, pid)
        p_sales = filter_sales_by_date_range(dataset["sales"], p_start, p_end, sid, pid)

        r_total = sum(s["quantity_sold"] for s in r_sales)
        p_total = sum(s["quantity_sold"] for s in p_sales)

        if p_total > 0 and r_total >= 10:
            growth = calculate_growth_percentage(r_total, p_total)
            if growth >= 80.0:
                prod = prod_map.get(pid, {"product_name": pid, "category": "General"})
                st = store_map.get(sid, {"store_name": sid})

                alerts.append({
                    "alert_id": f"SPIKE_{sid}_{pid}",
                    "alert_type": "SALES SPIKE",
                    "severity": "INFO",
                    "product_id": pid,
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "store_id": sid,
                    "store_name": st["store_name"],
                    "current_stock": inv["current_stock"],
                    "reorder_level": inv["reorder_level"],
                    "avg_daily_sales": round(r_total / 14.0, 2),
                    "days_remaining": calculate_days_remaining(inv["current_stock"], r_total / 14.0),
                    "metric_value": f"+{growth}% demand surge",
                    "why_it_matters": f"Recent 14-day demand surged to {r_total} units (up from {p_total} units in prior period).",
                    "recommended_action": "VERIFY DEMAND SUSTAINABILITY BEFORE PERMANENT ORDER INCREASE",
                    "evidence_summary": f"Prior 14d: {p_total} units | Recent 14d: {r_total} units | Surge: +{growth}%"
                })

    return alerts


def detect_sales_drop(dataset, store_id=None):
    """Detects significant sales drops (>40% drop comparing monthly sales)."""
    alerts = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s for s in dataset["stores"]}

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]

        curr_m = calculate_monthly_sales(dataset["sales"], store_id=sid, product_id=pid)
        prev_m = calculate_previous_month_sales(dataset["sales"], store_id=sid, product_id=pid)

        if prev_m >= 15:
            growth = calculate_growth_percentage(curr_m, prev_m)
            if growth <= -40.0:
                prod = prod_map.get(pid, {"product_name": pid, "category": "General"})
                st = store_map.get(sid, {"store_name": sid})

                alerts.append({
                    "alert_id": f"DROP_{sid}_{pid}",
                    "alert_type": "SALES DROP",
                    "severity": "WARNING",
                    "product_id": pid,
                    "product_name": prod["product_name"],
                    "category": prod["category"],
                    "store_id": sid,
                    "store_name": st["store_name"],
                    "current_stock": inv["current_stock"],
                    "reorder_level": inv["reorder_level"],
                    "avg_daily_sales": calculate_average_daily_sales(dataset["sales"], sid, pid, 30),
                    "days_remaining": calculate_days_remaining(inv["current_stock"], calculate_average_daily_sales(dataset["sales"], sid, pid, 30)),
                    "metric_value": f"{growth}% decline",
                    "why_it_matters": f"Monthly volume fell from {prev_m} units last month to {curr_m} units this month.",
                    "recommended_action": "CHECK PRICING, AVAILABILITY, & COMPETITOR FACTORS",
                    "evidence_summary": f"Previous Month: {prev_m} units | Current Month: {curr_m} units | Drop: {growth}%"
                })

    return alerts


def get_all_alerts(dataset, store_id=None):
    """Combines all alerts sorted strictly by operational urgency."""
    stockouts = detect_stockout_risk(dataset, store_id)
    overstocks = detect_overstock(dataset, store_id)
    spikes = detect_sales_spike(dataset, store_id)
    drops = detect_sales_drop(dataset, store_id)

    return stockouts + overstocks + drops + spikes


# ==============================================================================
# NEW NEXUS COMMAND CENTER DETERMINISTIC INTELLIGENCE FUNCTIONS
# ==============================================================================

def calculate_inventory_matrix(dataset):
    """
    Computes Store x Product Health Matrix for Command Center Overview.
    Health Status:
    - CRITICAL (Red): Coverage <= 7 days
    - WARNING (Orange): Coverage 8-14 days OR Overstock (>=90 days)
    - HEALTHY (Green): Coverage 15-89 days
    """
    stores = dataset["stores"]
    products = dataset["products"]
    inventory = dataset["inventory"]
    sales = dataset["sales"]

    matrix_rows = []
    for p in products:
        pid = p["product_id"]
        row = {
            "product_id": pid,
            "product_name": p["product_name"],
            "category": p["category"],
            "stores": {}
        }
        for st in stores:
            sid = st["store_id"]
            inv_item = next((i for i in inventory if i["product_id"] == pid and i["store_id"] == sid), None)
            if inv_item:
                stock = inv_item["current_stock"]
                avg_sales = calculate_average_daily_sales(sales, sid, pid, 30)
                cov = calculate_days_remaining(stock, avg_sales)

                if cov is not None and cov <= 7.0:
                    status = "CRITICAL"
                elif (cov is not None and cov <= 14.0) or (cov is not None and cov >= 90.0):
                    status = "WARNING"
                else:
                    status = "HEALTHY"

                row["stores"][sid] = {
                    "current_stock": stock,
                    "avg_daily_sales": avg_sales,
                    "coverage_days": cov,
                    "status": status
                }
            else:
                row["stores"][sid] = {"status": "N/A", "coverage_days": None}

        matrix_rows.append(row)

    return matrix_rows


def calculate_demand_forecast(dataset, store_id=None):
    """
    Computes 7-Day and 14-Day Demand Forecasts and Stock-Out Projections.
    Formula:
    7-Day Demand = 7 * Average Daily Sales (30d)
    14-Day Demand = 14 * Average Daily Sales (30d)
    Projected Stock 7d = Current Stock - 7-Day Demand
    """
    forecasts = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s["store_name"] for s in dataset["stores"]}
    latest_date_str = get_latest_date(dataset["sales"])
    latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]
        stock = inv["current_stock"]

        avg_daily = calculate_average_daily_sales(dataset["sales"], sid, pid, 30)
        demand_7d = round(avg_daily * 7.0, 1)
        demand_14d = round(avg_daily * 14.0, 1)
        projected_stock_7d = round(stock - demand_7d, 1)
        projected_stock_14d = round(stock - demand_14d, 1)

        cov_days = calculate_days_remaining(stock, avg_daily)
        if cov_days is not None and cov_days < 999:
            stockout_dt = latest_dt + timedelta(days=math.ceil(cov_days))
            stockout_date_str = stockout_dt.strftime("%b %d, %Y")
        else:
            stockout_date_str = "No Stockout Projected"

        if cov_days is not None and cov_days <= 7.0:
            status = "CRITICAL STOCK-OUT RISK"
        elif cov_days is not None and cov_days <= 14.0:
            status = "WARNING STOCK-OUT RISK"
        elif cov_days is not None and cov_days >= 90.0:
            status = "OVERSTOCK SURPLUS"
        else:
            status = "HEALTHY COVERAGE"

        prod = prod_map.get(pid, {"product_name": pid, "category": "General"})

        forecasts.append({
            "product_id": pid,
            "product_name": prod["product_name"],
            "category": prod["category"],
            "store_id": sid,
            "store_name": store_map.get(sid, sid),
            "current_stock": stock,
            "avg_daily_sales": avg_daily,
            "demand_7d": demand_7d,
            "demand_14d": demand_14d,
            "projected_stock_7d": projected_stock_7d,
            "projected_stock_14d": projected_stock_14d,
            "coverage_days": cov_days,
            "estimated_stockout_date": stockout_date_str,
            "projected_status": status
        })

    forecasts.sort(key=lambda x: x["coverage_days"] if x["coverage_days"] is not None else 999)
    return forecasts


def calculate_smart_reorders(dataset, store_id=None, target_coverage=14):
    """
    Computes Recommended Replenishment Quantity.
    Target Stock = Average Daily Sales * Target Coverage Days
    Recommended Reorder = max(0, Target Stock - Current Stock)
    """
    reorders = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s["store_name"] for s in dataset["stores"]}

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]
        stock = inv["current_stock"]

        avg_daily = calculate_average_daily_sales(dataset["sales"], sid, pid, 30)
        cov_days = calculate_days_remaining(stock, avg_daily)

        target_stock = round(avg_daily * float(target_coverage))
        recommended_reorder = max(0, target_stock - stock)

        if recommended_reorder > 0 or (cov_days is not None and cov_days <= 14.0):
            prod = prod_map.get(pid, {"product_name": pid, "category": "General"})

            if cov_days is not None and cov_days <= 7.0:
                timeline = "Replenish within 24 hours"
                urgency = "CRITICAL"
            elif cov_days is not None and cov_days <= 14.0:
                timeline = "Replenish within 48 hours"
                urgency = "WARNING"
            else:
                timeline = "Standard replenishment"
                urgency = "ROUTINE"

            reorders.append({
                "product_id": pid,
                "product_name": prod["product_name"],
                "category": prod["category"],
                "store_id": sid,
                "store_name": store_map.get(sid, sid),
                "current_stock": stock,
                "avg_daily_sales": avg_daily,
                "coverage_days": cov_days,
                "target_coverage_days": target_coverage,
                "target_stock": target_stock,
                "recommended_reorder": recommended_reorder,
                "action_timeline": timeline,
                "urgency": urgency,
                "formula_explanation": f"Target Stock ({target_stock}) = Avg Sales ({avg_daily}/day) × Target Coverage ({target_coverage} days). Recommended Reorder ({recommended_reorder}) = Target Stock ({target_stock}) - Current Stock ({stock})."
            })

    reorders.sort(key=lambda x: (x["urgency"] != "CRITICAL", x["coverage_days"] if x["coverage_days"] is not None else 999))
    return reorders


def calculate_smart_transfers(dataset):
    """
    Identifies Store-to-Store Transfer Opportunities.
    Detects where Store A has LOW stock (<=14d) AND Store B has EXCESS stock (>20d or >reorder level).
    """
    transfers = []
    prod_map = {p["product_id"]: p for p in dataset["products"]}
    store_map = {s["store_id"]: s["store_name"] for s in dataset["stores"]}
    products = dataset["products"]

    for p in products:
        pid = p["product_id"]
        p_name = p["product_name"]

        # Collect inventory per store for this product
        p_invs = []
        for inv in dataset["inventory"]:
            if inv["product_id"] == pid:
                avg = calculate_average_daily_sales(dataset["sales"], inv["store_id"], pid, 30)
                cov = calculate_days_remaining(inv["current_stock"], avg)
                p_invs.append({
                    "store_id": inv["store_id"],
                    "store_name": store_map.get(inv["store_id"], inv["store_id"]),
                    "current_stock": inv["current_stock"],
                    "avg_daily_sales": avg,
                    "coverage_days": cov,
                    "reorder_level": inv["reorder_level"]
                })

        # Identify deficit stores (low coverage) and surplus stores (high stock)
        deficits = [item for item in p_invs if item["coverage_days"] is not None and item["coverage_days"] <= 14.0]
        surpluses = [item for item in p_invs if item["current_stock"] > item["reorder_level"] and item["coverage_days"] is not None and item["coverage_days"] >= 20.0]

        for def_item in deficits:
            for sur_item in surpluses:
                if def_item["store_id"] != sur_item["store_id"]:
                    # Calculate safe surplus quantity to transfer
                    surplus_qty = sur_item["current_stock"] - sur_item["reorder_level"]
                    deficit_needed = round((14.0 - def_item["coverage_days"]) * def_item["avg_daily_sales"])
                    transfer_qty = max(5, min(surplus_qty, deficit_needed))

                    if transfer_qty > 0:
                        transfers.append({
                            "product_id": pid,
                            "product_name": p_name,
                            "category": p["category"],
                            "from_store_id": sur_item["store_id"],
                            "from_store_name": sur_item["store_name"],
                            "from_stock": sur_item["current_stock"],
                            "from_coverage": sur_item["coverage_days"],
                            "to_store_id": def_item["store_id"],
                            "to_store_name": def_item["store_name"],
                            "to_stock": def_item["current_stock"],
                            "to_coverage": def_item["coverage_days"],
                            "recommended_transfer_qty": transfer_qty,
                            "reason": f"{sur_item['store_name']} has surplus stock ({sur_item['current_stock']} units, {sur_item['coverage_days']}d coverage) while {def_item['store_name']} is at stockout risk ({def_item['current_stock']} units, {def_item['coverage_days']}d coverage)."
                        })

    transfers.sort(key=lambda x: x["to_coverage"])
    return transfers


def run_inventory_simulation(dataset, store_id, product_id, sales_change_pct, incoming_stock, target_days=14):
    """
    Non-mutating What-If Inventory Simulator calculation.
    """
    inv_item = next((i for i in dataset["inventory"] if i["product_id"] == product_id and i["store_id"] == store_id), None)
    if not inv_item:
        return {"error": "Selected store and product combination not found."}

    prod = next((p for p in dataset["products"] if p["product_id"] == product_id), None)
    store = next((s for s in dataset["stores"] if s["store_id"] == store_id), None)

    base_stock = inv_item["current_stock"]
    base_avg_sales = calculate_average_daily_sales(dataset["sales"], store_id, product_id, 30)

    # Dynamic scenario calculations
    sales_multiplier = 1.0 + (sales_change_pct / 100.0)
    simulated_daily_sales = max(0.1, round(base_avg_sales * sales_multiplier, 2))
    simulated_total_stock = base_stock + incoming_stock

    simulated_coverage_days = round(simulated_total_stock / simulated_daily_sales, 1)

    target_stock = round(simulated_daily_sales * float(target_days))
    additional_reorder_needed = max(0, target_stock - simulated_total_stock)

    if simulated_coverage_days <= 7.0:
        sim_risk = "CRITICAL STOCK-OUT RISK"
        sim_action = f"Add {additional_reorder_needed} additional units immediately to prevent stockout."
    elif simulated_coverage_days <= 14.0:
        sim_risk = "WARNING STOCK-OUT RISK"
        sim_action = f"Schedule replenishment of {additional_reorder_needed} units within 48 hours."
    elif simulated_coverage_days >= 90.0:
        sim_risk = "OVERSTOCK SURPLUS"
        sim_action = "Halt incoming orders and review promotional markdown options."
    else:
        sim_risk = "HEALTHY COVERAGE"
        sim_action = "Simulated scenario maintains safe inventory buffer."

    latest_dt = datetime.strptime(get_latest_date(dataset["sales"]), "%Y-%m-%d")
    projected_stockout_dt = latest_dt + timedelta(days=math.ceil(simulated_coverage_days))

    return {
        "is_simulation": True,
        "product_id": product_id,
        "product_name": prod["product_name"] if prod else product_id,
        "store_id": store_id,
        "store_name": store["store_name"] if store else store_id,
        "baseline": {
            "current_stock": base_stock,
            "avg_daily_sales": base_avg_sales,
            "coverage_days": calculate_days_remaining(base_stock, base_avg_sales)
        },
        "simulation_parameters": {
            "sales_change_pct": sales_change_pct,
            "incoming_stock": incoming_stock,
            "target_coverage_days": target_days
        },
        "simulated_results": {
            "simulated_daily_sales": simulated_daily_sales,
            "simulated_total_stock": simulated_total_stock,
            "simulated_coverage_days": simulated_coverage_days,
            "estimated_stockout_date": projected_stockout_dt.strftime("%b %d, %Y"),
            "risk_level": sim_risk,
            "recommended_action": sim_action,
            "additional_reorder_needed": additional_reorder_needed
        }
    }


def calculate_store_performance(dataset):
    """Computes store performance KPIs and comparisons."""
    stores_perf = []
    prod_count = len(dataset["products"])

    for st in dataset["stores"]:
        sid = st["store_id"]
        rev = calculate_total_revenue(dataset["sales"], store_id=sid)
        units = calculate_units_sold(dataset["sales"], store_id=sid)
        curr_m = calculate_monthly_sales(dataset["sales"], store_id=sid)
        prev_m = calculate_previous_month_sales(dataset["sales"], store_id=sid)
        growth = calculate_growth_percentage(curr_m, prev_m)

        stockout_alerts = detect_stockout_risk(dataset, store_id=sid, high_threshold=7.0)

        stores_perf.append({
            "store_id": sid,
            "store_name": st["store_name"],
            "city": st["city"],
            "region": st["region"],
            "revenue": rev,
            "units_sold": units,
            "active_products": prod_count,
            "low_stock_count": len(stockout_alerts),
            "monthly_sales": curr_m,
            "previous_monthly_sales": prev_m,
            "sales_growth_pct": growth
        })

    stores_perf.sort(key=lambda x: x["revenue"], reverse=True)
    return stores_perf


def calculate_product_performance(dataset, store_id=None):
    """Calculates performance details for every product."""
    products_perf = []
    store_map = {s["store_id"]: s["store_name"] for s in dataset["stores"]}

    for inv in dataset["inventory"]:
        if store_id and inv["store_id"] != store_id:
            continue
        pid = inv["product_id"]
        sid = inv["store_id"]

        avg_daily = calculate_average_daily_sales(dataset["sales"], sid, pid, 30)
        days_left = calculate_days_remaining(inv["current_stock"], avg_daily)
        curr_m = calculate_monthly_sales(dataset["sales"], sid, pid)
        prev_m = calculate_previous_month_sales(dataset["sales"], sid, pid)
        growth = calculate_growth_percentage(curr_m, prev_m)

        if days_left is not None and days_left <= 7.0:
            risk = "CRITICAL STOCK-OUT"
            action = "Reorder immediately"
        elif days_left is not None and days_left <= 14.0:
            risk = "WARNING STOCK-OUT"
            action = "Schedule replenishment"
        elif days_left is not None and days_left >= 90.0:
            risk = "OVERSTOCK"
            action = "Review stock & offer promotion"
        else:
            risk = "HEALTHY"
            action = "Maintain current monitoring"

        prod_info = next((p for p in dataset["products"] if p["product_id"] == pid), None)
        pname = prod_info["product_name"] if prod_info else pid
        cat = prod_info["category"] if prod_info else "General"

        products_perf.append({
            "product_id": pid,
            "product_name": pname,
            "category": cat,
            "store_id": sid,
            "store_name": store_map.get(sid, sid),
            "current_stock": inv["current_stock"],
            "reorder_level": inv["reorder_level"],
            "unit_cost": inv["unit_cost"],
            "selling_price": inv["selling_price"],
            "avg_daily_sales": avg_daily,
            "days_remaining": days_left,
            "current_month_sales": curr_m,
            "previous_month_sales": prev_m,
            "growth_pct": growth,
            "risk_level": risk,
            "recommended_action": action
        })

    return products_perf


def parse_question_intent(question, dataset):
    """
    Parses natural language question to extract relevant deterministic evidence context.
    Matches queries against product names, categories, store names, operational topics,
    and explicitly handles unanswerable or zero-match queries WITHOUT defaulting to unrelated products.
    """
    q_raw = question.strip()
    q_lower = q_raw.lower()

    # 1. UNANSWERABLE METRIC CHECKS
    if any(k in q_lower for k in ["profit", "margin", "net profit", "highest profit", "most profitable"]):
        return {
            "unanswerable": True,
            "reason": "Profit or margin data is not present in the current dataset (only unit cost, selling price, and revenue are tracked).",
            "topic": "PROFIT"
        }

    if any(k in q_lower for k in ["2030", "forecast 20", "next year", "future prediction", "sales in 20"]):
        return {
            "unanswerable": True,
            "reason": "The dataset contains historical sales data for 90 days only and does not contain predictive forecasting parameters for future years.",
            "topic": "FORECAST"
        }

    if any(k in q_lower for k in ["competitor", "market share", "discount code", "promotion campaign", "ad spend"]):
        return {
            "unanswerable": True,
            "reason": "The dataset does not contain competitor pricing, marketing campaign, or promotion tracking data.",
            "topic": "EXTERNAL_MARKETING"
        }

    # 2. INTENT: STOCK-OUT / RUNNING OUT / AT RISK
    if any(k in q_lower for k in ["run out", "running out", "stockout", "stock-out", "low stock", "reorder", "depleted", "at risk", "less than 5", "critical"]):
        stockout_alerts = detect_stockout_risk(dataset)
        return {
            "intent": "STOCKOUT_RISK",
            "title": "Products at Stock-Out Risk",
            "alerts": stockout_alerts[:6],
            "summary": f"Found {len(stockout_alerts)} products with low stock coverage."
        }

    # 3. INTENT: OVERSTOCK / SLOW MOVING
    if any(k in q_lower for k in ["overstock", "overstocked", "excess", "slow moving", "too much stock"]):
        overstock_alerts = detect_overstock(dataset)
        return {
            "intent": "OVERSTOCK",
            "title": "Overstocked & Slow-Moving Products",
            "alerts": overstock_alerts[:6],
            "summary": f"Found {len(overstock_alerts)} overstocked products."
        }

    # 4. INTENT: ATTENTION TODAY
    if any(k in q_lower for k in ["attention", "need attention", "today", "alert", "priority"]):
        all_alerts = get_all_alerts(dataset)
        return {
            "intent": "ATTENTION_TODAY",
            "title": "Products Requiring Immediate Attention Today",
            "alerts": all_alerts[:8],
            "summary": f"Found {len(all_alerts)} items requiring manager attention."
        }

    # 5. INTENT: STORE PERFORMANCE / BEST STORE
    if any(k in q_lower for k in ["best store", "top store", "performing best", "store performance", "compare store", "highest revenue store"]):
        stores_perf = calculate_store_performance(dataset)
        top_store = stores_perf[0]
        return {
            "intent": "STORE_PERFORMANCE",
            "title": "Store Performance Ranking",
            "top_store": top_store,
            "all_stores": stores_perf,
            "summary": f"Top store is {top_store['store_name']} with Total Revenue of ₹{top_store['revenue']:,.2f}."
        }

    # 6. INTENT: STORE-TO-STORE TRANSFERS
    if any(k in q_lower for k in ["transfer", "where should stock be transferred", "inter-store", "surplus transfer"]):
        transfers = calculate_smart_transfers(dataset)
        return {
            "intent": "STORE_TRANSFERS",
            "title": "Store-to-Store Transfer Opportunities",
            "transfers": transfers[:6],
            "summary": f"Found {len(transfers)} store-to-store transfer opportunities."
        }

    # 7. INTENT: REORDER & REPLENISHMENT
    if any(k in q_lower for k in ["what should we reorder", "recommended reorder", "replenishment"]):
        reorders = calculate_smart_reorders(dataset, target_coverage=14)
        return {
            "intent": "REORDER_ENGINE",
            "title": "Recommended Replenishment Orders",
            "reorders": reorders[:6],
            "summary": f"Found {len(reorders)} recommended replenishment orders."
        }

    # 8. INTENT: SALES PERFORMANCE / MONTH PERFORMANCE
    if any(k in q_lower for k in ["sales perform", "month perform", "how did sales", "overall performance", "monthly sales", "total sales"]):
        stores_perf = calculate_store_performance(dataset)
        total_rev = calculate_total_revenue(dataset["sales"])
        total_units = calculate_units_sold(dataset["sales"])
        return {
            "intent": "SALES_PERFORMANCE",
            "title": "Retail Sales Performance",
            "total_revenue": total_rev,
            "units_sold": total_units,
            "stores": stores_perf,
            "summary": f"Total revenue across 90 days is ₹{total_rev:,.2f} over {total_units} units sold."
        }

    # 9. INTENT: SALES SPIKE / INCREASE
    if any(k in q_lower for k in ["spike", "surge", "sales increase", "sales spike", "demand surge", "increased", "jumped"]):
        spike_alerts = detect_sales_spike(dataset)
        return {
            "intent": "SALES_SPIKE",
            "title": "Products with Sales Spikes",
            "alerts": spike_alerts[:6],
            "summary": f"Found {len(spike_alerts)} products with demand spikes."
        }

    # 10. INTENT: SALES DROP / DECREASE
    if any(k in q_lower for k in ["sales drop", "sales fall", "sales fell", "sales decline", "sales drop", "decline", "dropped", "declined"]):
        target_prod = None
        for p in dataset["products"]:
            if p["product_name"].lower() in q_lower or p["product_id"].lower() in q_lower:
                target_prod = p
                break

        if target_prod:
            pid = target_prod["product_id"]
            pname = target_prod["product_name"]
            sid = "ST01"
            curr_m = calculate_monthly_sales(dataset["sales"], sid, pid)
            prev_m = calculate_previous_month_sales(dataset["sales"], sid, pid)
            growth = calculate_growth_percentage(curr_m, prev_m)

            return {
                "intent": "SPECIFIC_PRODUCT_DROP",
                "product_name": pname,
                "product_id": pid,
                "previous_month_sales": prev_m,
                "current_month_sales": curr_m,
                "decline_pct": growth,
                "cause_known": False,
                "cause_explanation": f"The available dataset confirms a decline of {abs(growth)}%, but does not contain promotion, pricing, competitor, or customer traffic records, so the exact root cause cannot be established from this dataset."
            }

        drop_alerts = detect_sales_drop(dataset)
        return {
            "intent": "SALES_DROP",
            "title": "Products with Significant Sales Decline",
            "alerts": drop_alerts[:6],
            "summary": f"Found {len(drop_alerts)} products experiencing sales drop."
        }

    # 11. INTENT: PRODUCT / CATEGORY / INVENTORY SEARCH / LOOKUP
    search_terms = q_lower.split()
    matched_products = []
    
    category_synonyms = {
        "computers": "electronics",
        "computer": "electronics",
        "pc": "electronics",
        "laptops": "accessories",
        "gadgets": "electronics",
        "phones": "accessories",
        "clothes": "lifestyle",
        "wearing": "lifestyle"
    }

    expanded_terms = set(search_terms)
    for term in search_terms:
        if term in category_synonyms:
            expanded_terms.add(category_synonyms[term])

    all_prods_perf = calculate_product_performance(dataset)

    for p in all_prods_perf:
        p_name_lower = p["product_name"].lower()
        p_cat_lower = p["category"].lower()
        p_id_lower = p["product_id"].lower()

        if any(term in p_name_lower or term in p_cat_lower or term in p_id_lower for term in expanded_terms):
            matched_products.append(p)

    if matched_products:
        return {
            "intent": "PRODUCT_LOOKUP",
            "title": f"Products Matching '{q_raw}'",
            "matched_products": matched_products[:8],
            "summary": f"Found {len(matched_products)} products matching '{q_raw}' in the retail catalogue."
        }

    # 12. NO MATCHING PRODUCT OR CATEGORY
    if len(search_terms) <= 3 and not any(k in q_lower for k in ["what", "which", "how", "why", "show", "tell", "explain"]):
        return {
            "no_match": True,
            "reason": f"I couldn't find a matching product or category in the available retail data for '{q_raw}'.",
            "topic": "PRODUCT_NOT_FOUND"
        }

    # 13. UNKNOWN / AMBIGUOUS GENERAL QUESTION
    return {
        "unknown_question": True,
        "reason": f"I don't have enough information to answer '{q_raw}' from the available retail data.",
        "available_info": "Available stores: Chennai Central, Coimbatore Main, Madurai Plaza. Product categories: Electronics, Accessories, Home, Kitchen, Personal Care, Stationery, Grocery, Lifestyle.",
        "topic": "AMBIGUOUS"
    }
