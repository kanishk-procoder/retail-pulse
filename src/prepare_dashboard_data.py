import os
import json
import pandas as pd
import numpy as np

def run_dashboard_prep():
    print("==================================================")
    print("RETAILPULSE: STEP 7 - DASHBOARD DATA PREPARATION")
    print("==================================================")
    
    os.makedirs("dashboard/data", exist_ok=True)
    
    # 1. Load clean transactions
    clean_path = "data/processed/cleaned_transactions.parquet"
    if not os.path.exists(clean_path):
        clean_path = "data/processed/cleaned_transactions.csv"
    df = pd.read_parquet(clean_path) if clean_path.endswith('.parquet') else pd.read_csv(clean_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 2. Executive KPIs
    total_rev = float(df['TotalAmount'].sum())
    total_customers = int(df['CustomerID'].nunique())
    total_orders = int(df['Invoice'].nunique())
    total_units = int(df['Quantity'].sum())
    aov = round(total_rev / total_orders, 2)
    
    # Churn KPIs
    churn_df = pd.read_csv("data/processed/customer_churn_scored.csv")
    churn_rate = round(float(churn_df['is_churned'].mean() * 100), 1)
    high_risk_custs = int((churn_df['churn_risk_category'] == 'High Risk').sum())
    
    # Forecast KPIs
    with open("reports/metrics/forecasting_metrics.json", "r") as f:
        forecasting_metrics = json.load(f)
    best_forecast_mape = min([m['MAPE'] for m in forecasting_metrics])
    
    # Inventory KPIs
    inv_df = pd.read_csv("data/processed/inventory_recommendations.csv")
    crit_count = int((inv_df['stock_status'] == 'Critical Risk').sum())
    reorder_count = int((inv_df['stock_status'] == 'Reorder Triggered').sum())
    overstock_count = int((inv_df['stock_status'] == 'Overstocked').sum())
    
    kpi_payload = {
        "total_revenue": total_rev,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_units_sold": total_units,
        "average_order_value": aov,
        "churn_rate_pct": churn_rate,
        "high_risk_customers": high_risk_custs,
        "best_forecaster_mape": best_forecast_mape,
        "critical_inventory_items": crit_count,
        "reorder_triggered_items": reorder_count,
        "overstocked_items": overstock_count
    }
    
    with open("dashboard/data/kpis.json", "w") as f:
        json.dump(kpi_payload, f, indent=4)
        
    # 3. Time Series Trends
    daily_trend = df.groupby(df['InvoiceDate'].dt.date).agg({
        'TotalAmount': 'sum',
        'Invoice': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    daily_trend.columns = ['Date', 'Revenue', 'Orders', 'Units']
    daily_trend['Date'] = daily_trend['Date'].astype(str)
    daily_trend.to_csv("dashboard/data/daily_sales.csv", index=False)
    
    # 4. Country Revenue Breakdown
    country_summary = df.groupby('Country').agg({
        'TotalAmount': 'sum',
        'CustomerID': 'nunique',
        'Invoice': 'nunique'
    }).reset_index().sort_values('TotalAmount', ascending=False)
    country_summary.columns = ['Country', 'TotalRevenue', 'UniqueCustomers', 'Orders']
    country_summary['RevenueShare'] = (country_summary['TotalRevenue'] / total_rev * 100).round(2)
    country_summary.to_csv("dashboard/data/country_distribution.csv", index=False)
    
    # 5. Top Products
    top_prods = df.groupby(['StockCode', 'Description']).agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'Price': 'mean'
    }).reset_index().sort_values('TotalAmount', ascending=False).head(50)
    top_prods.columns = ['StockCode', 'Description', 'TotalRevenue', 'QuantitySold', 'AvgPrice']
    top_prods.to_csv("dashboard/data/top_products.csv", index=False)
    
    # 6. Customer Segments
    seg_df = pd.read_csv("data/processed/customer_segments.csv")
    seg_summary = seg_df.groupby('Final_Segment').agg({
        'CustomerID': 'count',
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': ['mean', 'sum']
    }).reset_index()
    seg_summary.columns = ['Segment', 'CustomerCount', 'AvgRecency', 'AvgFrequency', 'AvgMonetary', 'TotalRevenue']
    seg_summary['RevenueShare'] = (seg_summary['TotalRevenue'] / total_rev * 100).round(2)
    seg_summary.to_csv("dashboard/data/segmentation_summary.csv", index=False)
    
    # Sample 1000 customers for fast 3D Plotly rendering
    seg_df.sample(min(1500, len(seg_df)), random_state=42).to_csv("dashboard/data/customer_segments_sample.csv", index=False)
    
    # 7. Copy forecast comparison
    fc_pred = pd.read_csv("data/predictions/forecasting_comparison.csv")
    fc_pred.to_csv("dashboard/data/forecasting_comparison.csv", index=False)
    
    # 8. Copy churn predictions & SHAP
    churn_sample = churn_df.sort_values('churn_risk_probability', ascending=False).head(200)
    churn_sample.to_csv("dashboard/data/churn_top_risk.csv", index=False)
    
    shap_df = pd.read_csv("reports/metrics/churn_shap_importance.csv")
    shap_df.to_csv("dashboard/data/shap_importance.csv", index=False)
    
    # 9. Top critical inventory items
    crit_inv = inv_df[inv_df['stock_status'].isin(['Critical Risk', 'Reorder Triggered'])].sort_values('reorder_point', ascending=False).head(100)
    crit_inv.to_csv("dashboard/data/inventory_alerts.csv", index=False)
    
    # 10. Master Leaderboards
    with open("reports/metrics/segmentation_metrics.json") as f:
        seg_m = json.load(f)
    with open("reports/metrics/forecasting_metrics.json") as f:
        fore_m = json.load(f)
    with open("reports/metrics/churn_metrics.json") as f:
        churn_m = json.load(f)
        
    master_leaderboard = {
        "segmentation": seg_m,
        "forecasting": fore_m,
        "churn": churn_m
    }
    with open("dashboard/data/master_leaderboards.json", "w") as f:
        json.dump(master_leaderboard, f, indent=4)
        
    print("Dashboard data files generated in dashboard/data/ [OK]")
    print("==================================================")

if __name__ == "__main__":
    run_dashboard_prep()

