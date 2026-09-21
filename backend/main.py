import os
import json
import math
import numpy as np
import pandas as pd
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="RetailPulse AI Platform REST API",
    description="Production-grade AI API for Demand Forecasting, Customer Segmentation, Churn Prevention, and Inventory Optimization.",
    version="2.0.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_DATA_DIR = os.path.join(BASE_DIR, "dashboard", "data")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# In-Memory Cache
DATA_CACHE = {}

def load_data():
    """Load and cache pre-aggregated analytical datasets into memory."""
    print("Loading RetailPulse datasets into memory cache...")
    
    # 1. KPIs
    kpis_path = os.path.join(DASHBOARD_DATA_DIR, "kpis.json")
    if os.path.exists(kpis_path):
        with open(kpis_path, "r", encoding="utf-8") as f:
            DATA_CACHE["kpis"] = json.load(f)
            
    # 2. Master Leaderboards
    lead_path = os.path.join(DASHBOARD_DATA_DIR, "master_leaderboards.json")
    if os.path.exists(lead_path):
        with open(lead_path, "r", encoding="utf-8") as f:
            DATA_CACHE["leaderboards"] = json.load(f)
            
    # 3. Daily Sales Time Series
    daily_path = os.path.join(DASHBOARD_DATA_DIR, "daily_sales.csv")
    if os.path.exists(daily_path):
        DATA_CACHE["daily_sales"] = pd.read_csv(daily_path)
        
    # 4. Country Distribution
    country_path = os.path.join(DASHBOARD_DATA_DIR, "country_distribution.csv")
    if os.path.exists(country_path):
        DATA_CACHE["country_distribution"] = pd.read_csv(country_path)
        
    # 5. Top Products
    top_prod_path = os.path.join(DASHBOARD_DATA_DIR, "top_products.csv")
    if os.path.exists(top_prod_path):
        DATA_CACHE["top_products"] = pd.read_csv(top_prod_path)
        
    # 6. Customer Segments Summary & Sample
    seg_sum_path = os.path.join(DASHBOARD_DATA_DIR, "segmentation_summary.csv")
    if os.path.exists(seg_sum_path):
        DATA_CACHE["segmentation_summary"] = pd.read_csv(seg_sum_path)
        
    cust_sample_path = os.path.join(DASHBOARD_DATA_DIR, "customer_segments_sample.csv")
    if os.path.exists(cust_sample_path):
        DATA_CACHE["customer_segments_sample"] = pd.read_csv(cust_sample_path)
        
    # 7. Full RFM Features
    rfm_path = os.path.join(PROCESSED_DATA_DIR, "rfm_features.csv")
    if os.path.exists(rfm_path):
        DATA_CACHE["rfm_features"] = pd.read_csv(rfm_path)
        
    # 8. Forecasting Comparison
    fore_path = os.path.join(DASHBOARD_DATA_DIR, "forecasting_comparison.csv")
    if os.path.exists(fore_path):
        DATA_CACHE["forecasting_comparison"] = pd.read_csv(fore_path)
        
    # 9. Churn Top Risk & SHAP
    churn_path = os.path.join(DASHBOARD_DATA_DIR, "churn_top_risk.csv")
    if os.path.exists(churn_path):
        DATA_CACHE["churn_top_risk"] = pd.read_csv(churn_path)
        
    shap_path = os.path.join(DASHBOARD_DATA_DIR, "shap_importance.csv")
    if os.path.exists(shap_path):
        DATA_CACHE["shap_importance"] = pd.read_csv(shap_path)
        
    # 10. Inventory Recommendations (4,305 SKUs)
    inv_path = os.path.join(PROCESSED_DATA_DIR, "inventory_recommendations.csv")
    if os.path.exists(inv_path):
        DATA_CACHE["inventory_recommendations"] = pd.read_csv(inv_path)
        
    print("RetailPulse datasets loaded successfully [OK]")

load_data()

# -----------------------------------------------------------------------------
# PYDANTIC SCHEMAS
# -----------------------------------------------------------------------------
class ForecastSimulationRequest(BaseModel):
    demand_shock_pct: float = 0.0      # e.g., +15.0 for +15%, -10.0 for -10%
    marketing_multiplier: float = 1.0  # e.g., 1.1 for 10% marketing lift
    model_choice: str = "LSTM"         # "LSTM", "XGBoost", "Ensemble", "Prophet"

class InventoryRecalculateRequest(BaseModel):
    service_level: float = 0.95        # 0.90 to 0.99
    lead_time_days: int = 7
    order_cost: float = 15.0
    holding_rate: float = 0.20

# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """Health status and dataset availability verification."""
    return {
        "status": "online",
        "service": "RetailPulse AI REST API",
        "version": "2.0.0",
        "cached_keys": list(DATA_CACHE.keys()),
        "total_active_skus": len(DATA_CACHE.get("inventory_recommendations", [])),
        "total_active_customers": len(DATA_CACHE.get("rfm_features", []))
    }

@app.get("/api/overview")
def get_overview():
    """High-level business performance KPIs, sales trajectories, and top dimensions."""
    kpis = DATA_CACHE.get("kpis", {})
    daily_sales = DATA_CACHE.get("daily_sales", pd.DataFrame()).copy()
    countries = DATA_CACHE.get("country_distribution", pd.DataFrame()).copy()
    top_prods = DATA_CACHE.get("top_products", pd.DataFrame()).copy()
    
    # Clean records for JSON serialization
    daily_records = daily_sales.tail(90).to_dict(orient="records") if not daily_sales.empty else []
    country_records = countries.head(10).to_dict(orient="records") if not countries.empty else []
    product_records = top_prods.head(10).to_dict(orient="records") if not top_prods.empty else []
    
    return {
        "kpis": kpis,
        "daily_sales_trend": daily_records,
        "top_countries": country_records,
        "top_products": product_records
    }

@app.get("/api/segmentation/summary")
def get_segmentation_summary():
    """Customer segments distribution and behavioral profiles."""
    seg_df = DATA_CACHE.get("segmentation_summary", pd.DataFrame()).copy()
    if seg_df.empty:
        raise HTTPException(status_code=404, detail="Segmentation summary data not found")
    return {
        "segments": seg_df.to_dict(orient="records")
    }

@app.get("/api/segmentation/customers")
def get_segmentation_sample(limit: int = 400):
    """Sampled customers with RFM coordinates and 2D PCA projections."""
    sample_df = DATA_CACHE.get("customer_segments_sample", pd.DataFrame()).copy()
    if sample_df.empty:
        rfm_df = DATA_CACHE.get("rfm_features", pd.DataFrame()).copy()
        if rfm_df.empty:
            raise HTTPException(status_code=404, detail="Customer data not found")
        sample_df = rfm_df.sample(min(limit, len(rfm_df)), random_state=42)
    return {
        "count": len(sample_df),
        "customers": sample_df.head(limit).to_dict(orient="records")
    }

@app.get("/api/segmentation/customer/{customer_id}")
def get_customer_profile(customer_id: int):
    """Specific customer profile lookup with score breakdown and retention playbook."""
    rfm_df = DATA_CACHE.get("rfm_features", pd.DataFrame())
    if rfm_df.empty:
        raise HTTPException(status_code=404, detail="Customer dataset not found")
        
    cust = rfm_df[rfm_df["CustomerID"] == customer_id]
    if cust.empty:
        raise HTTPException(status_code=404, detail=f"Customer ID {customer_id} not found in records")
        
    cust_data = cust.iloc[0].to_dict()
    
    # Prescriptive Action Playbook based on Segment
    playbooks = {
        "Champions": "VIP concierge, sneak peek product launches, exclusive reward tiers, zero aggressive discounting.",
        "Loyal Customers": "Loyalty point multipliers, cross-sell high-affinity accessories, referral incentives.",
        "Promising / New": "Onboarding nurture sequence, post-purchase check-in, 10% coupon on second order.",
        "At Risk": "Proactive outreach from support, personalized win-back offer, re-engagement email sequence.",
        "Lost / Inactive": "Re-activation clearance campaigns or suppress ad spend to conserve marketing budget."
    }
    cust_data["retention_playbook"] = playbooks.get(cust_data.get("RFM_Segment"), "Standard engagement campaign.")
    
    return cust_data

@app.get("/api/forecasting/models")
def get_forecasting_data():
    """30-day holdout ground truth and predictions across all 7 forecasting architectures."""
    fore_df = DATA_CACHE.get("forecasting_comparison", pd.DataFrame()).copy()
    if fore_df.empty:
        raise HTTPException(status_code=404, detail="Forecasting data not found")
        
    leaderboard = DATA_CACHE.get("leaderboards", {}).get("forecasting", [])
    
    return {
        "dates": fore_df["Date"].tolist(),
        "trajectory": fore_df.to_dict(orient="records"),
        "models_available": [c for c in fore_df.columns if c not in ["Date", "Actual"]],
        "metrics_leaderboard": leaderboard
    }

@app.post("/api/forecasting/simulate")
def simulate_forecast(req: ForecastSimulationRequest):
    """Interactive What-If demand shock and marketing lift simulation."""
    fore_df = DATA_CACHE.get("forecasting_comparison", pd.DataFrame()).copy()
    if fore_df.empty:
        raise HTTPException(status_code=404, detail="Forecasting data not found")
        
    model_col = req.model_choice if req.model_choice in fore_df.columns else "LSTM"
    baseline = fore_df[model_col].values
    
    # Calculate simulation multiplier
    shock_mult = 1.0 + (req.demand_shock_pct / 100.0)
    total_mult = shock_mult * req.marketing_multiplier
    
    simulated_values = (baseline * total_mult).round(2)
    lower_bound = (simulated_values * 0.85).round(2)
    upper_bound = (simulated_values * 1.15).round(2)
    
    result = []
    for d, b, s, l, u in zip(fore_df["Date"], baseline, simulated_values, lower_bound, upper_bound):
        result.append({
            "Date": d,
            "Baseline": float(b),
            "Simulated": float(s),
            "Lower_Bound": float(l),
            "Upper_Bound": float(u)
        })
        
    total_baseline_rev = float(np.sum(baseline))
    total_simulated_rev = float(np.sum(simulated_values))
    revenue_delta = total_simulated_rev - total_baseline_rev
    
    return {
        "model_used": model_col,
        "total_baseline_revenue": round(total_baseline_rev, 2),
        "total_simulated_revenue": round(total_simulated_rev, 2),
        "revenue_delta": round(revenue_delta, 2),
        "pct_change": round((revenue_delta / total_baseline_rev) * 100, 2) if total_baseline_rev > 0 else 0,
        "simulated_trajectory": result
    }

@app.get("/api/churn/summary")
def get_churn_summary():
    """Customer churn risk tier distribution, key metrics, and SHAP explainability."""
    churn_df = DATA_CACHE.get("churn_top_risk", pd.DataFrame()).copy()
    shap_df = DATA_CACHE.get("shap_importance", pd.DataFrame()).copy()
    leaderboard = DATA_CACHE.get("leaderboards", {}).get("churn", [])
    
    # Summary Tiers
    tiers = {
        "High Risk (>70%)": int(len(churn_df[churn_df["churn_probability"] >= 0.70])),
        "Medium Risk (40-70%)": int(len(churn_df[(churn_df["churn_probability"] >= 0.40) & (churn_df["churn_probability"] < 0.70)])),
        "Low Risk (<40%)": int(len(churn_df[churn_df["churn_probability"] < 0.40]))
    }
    
    return {
        "risk_distribution": tiers,
        "shap_importance": shap_df.to_dict(orient="records") if not shap_df.empty else [],
        "metrics_leaderboard": leaderboard
    }

@app.get("/api/churn/high-risk")
def get_churn_high_risk(page: int = 1, page_size: int = 25, search: Optional[str] = None):
    """Paginated list of prioritized high-risk churn customers."""
    churn_df = DATA_CACHE.get("churn_top_risk", pd.DataFrame()).copy()
    if churn_df.empty:
        raise HTTPException(status_code=404, detail="Churn risk data not found")
        
    if search:
        churn_df = churn_df[churn_df["CustomerID"].astype(str).str.contains(search, case=False)]
        
    total_count = len(churn_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    items = churn_df.iloc[start_idx:end_idx].to_dict(orient="records")
    
    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_count / page_size) if page_size > 0 else 1,
        "customers": items
    }

@app.get("/api/inventory/summary")
def get_inventory_summary():
    """Prescriptive inventory optimization breakdown and working capital exposure."""
    inv_df = DATA_CACHE.get("inventory_recommendations", pd.DataFrame())
    if inv_df.empty:
        raise HTTPException(status_code=404, detail="Inventory data not found")
        
    status_counts = inv_df["stock_status"].value_counts().to_dict()
    
    # Capital calculations
    critical_df = inv_df[inv_df["stock_status"] == "Critical Stock"]
    overstocked_df = inv_df[inv_df["stock_status"] == "Overstocked"]
    
    capital_at_risk = float((critical_df["reorder_point"] * critical_df["avg_price"]).sum())
    capital_overstocked = float((overstocked_df["current_stock"] * overstocked_df["avg_price"]).sum())
    
    return {
        "total_active_skus": len(inv_df),
        "status_breakdown": status_counts,
        "capital_at_risk": round(capital_at_risk, 2),
        "capital_overstocked": round(capital_overstocked, 2),
        "reorder_triggered_count": int(status_counts.get("Reorder Triggered", 0) + status_counts.get("Critical Stock", 0))
    }

@app.get("/api/inventory/items")
def get_inventory_items(
    page: int = 1,
    page_size: int = 30,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Filterable, sortable, paginated catalog of all 4,305 active SKUs."""
    inv_df = DATA_CACHE.get("inventory_recommendations", pd.DataFrame()).copy()
    if inv_df.empty:
        raise HTTPException(status_code=404, detail="Inventory data not found")
        
    if status and status != "All":
        inv_df = inv_df[inv_df["stock_status"].str.lower() == status.lower()]
        
    if search:
        s_lower = search.lower()
        inv_df = inv_df[
            inv_df["StockCode"].astype(str).str.lower().str.contains(s_lower) |
            inv_df["Description"].astype(str).str.lower().str.contains(s_lower)
        ]
        
    total_count = len(inv_df)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    items = inv_df.iloc[start_idx:end_idx].to_dict(orient="records")
    
    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total_count / page_size) if page_size > 0 else 1,
        "items": items
    }

@app.post("/api/inventory/recalculate")
def recalculate_inventory_policies(req: InventoryRecalculateRequest):
    """Dynamic recalculation of Safety Stock, ROP, and EOQ based on customized Service Level."""
    inv_df = DATA_CACHE.get("inventory_recommendations", pd.DataFrame()).copy()
    if inv_df.empty:
        raise HTTPException(status_code=404, detail="Inventory data not found")
        
    # Standard normal Z-score lookup based on Service Level
    z_table = {
        0.90: 1.282,
        0.95: 1.645,
        0.98: 2.054,
        0.99: 2.326
    }
    # Closest match
    closest_sl = min(z_table.keys(), key=lambda k: abs(k - req.service_level))
    Z = z_table[closest_sl]
    L = req.lead_time_days
    S = req.order_cost
    H_rate = req.holding_rate
    
    # Recalculate
    inv_df["safety_stock"] = np.ceil(Z * inv_df["demand_std"] * np.sqrt(L)).astype(int)
    inv_df["reorder_point"] = np.ceil((inv_df["avg_daily_demand"] * L) + inv_df["safety_stock"]).astype(int)
    
    # EOQ: sqrt((2 * D * S) / H)
    annual_demand = inv_df["avg_daily_demand"] * 365
    holding_cost = (inv_df["avg_price"] * H_rate).clip(lower=0.5)
    inv_df["eoq"] = np.ceil(np.sqrt((2 * annual_demand * S) / holding_cost)).astype(int)
    
    # Update Status
    conditions = [
        inv_df["current_stock"] <= inv_df["safety_stock"],
        inv_df["current_stock"] <= inv_df["reorder_point"],
        inv_df["current_stock"] >= (inv_df["reorder_point"] + inv_df["eoq"])
    ]
    choices = ["Critical Stock", "Reorder Triggered", "Overstocked"]
    inv_df["stock_status"] = np.select(conditions, choices, default="Optimal")
    
    status_counts = inv_df["stock_status"].value_counts().to_dict()
    
    return {
        "applied_service_level": req.service_level,
        "z_score_used": Z,
        "lead_time_days": L,
        "status_breakdown": status_counts,
        "sample_updated_items": inv_df.head(10).to_dict(orient="records")
    }

@app.get("/api/leaderboard")
def get_master_leaderboard():
    """All 18 evaluated models across Segmentation, Forecasting, and Churn."""
    lead = DATA_CACHE.get("leaderboards", {})
    return lead

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

