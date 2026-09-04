from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Store:
    store_id: str
    store_name: str
    city: str
    region: str

@dataclass
class Product:
    product_id: str
    product_name: str
    category: str

@dataclass
class InventoryItem:
    store_id: str
    product_id: str
    current_stock: int
    reorder_level: int
    unit_cost: float
    selling_price: float

@dataclass
class Alert:
    alert_id: str
    alert_type: str  # HIGH_STOCK_OUT, MEDIUM_STOCK_OUT, OVERSTOCK, SALES_SPIKE, SALES_DROP
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    category: str
    current_stock: int
    avg_daily_sales: float
    days_remaining: Optional[float]
    metric_value: str
    why_it_matters: str
    recommended_action: str
    evidence_summary: str

@dataclass
class CopilotResponse:
    answer: str
    key_numbers: List[Dict[str, Any]]
    evidence: str
    recommendation: str
    assumptions_limitations: str
    is_unanswerable: bool = False
