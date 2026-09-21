import os
import pandas as pd
import numpy as np

def run_inventory_optimization():
    print("==================================================")
    print("RETAILPULSE: STEP 6 - INVENTORY OPTIMIZATION")
    print("==================================================")
    
    prod_path = os.path.join("data", "processed", "product_features.csv")
    df = pd.read_csv(prod_path)
    
    # Target 95% service level (Z = 1.65)
    Z = 1.65
    lead_time_days = 7.0  # Assumed standard supplier lead time
    ordering_cost_per_order = 15.0  # £15 administration & freight fee
    holding_cost_annual_rate = 0.20  # 20% of unit price per year
    
    # 1. Safety Stock
    # SS = Z * sigma_d * sqrt(L)
    df['safety_stock'] = np.ceil(Z * df['demand_std'] * np.sqrt(lead_time_days)).astype(int)
    
    # 2. Reorder Point (ROP)
    # ROP = (avg_daily_demand * L) + SS
    df['reorder_point'] = np.ceil((df['avg_daily_demand'] * lead_time_days) + df['safety_stock']).astype(int)
    
    # 3. Economic Order Quantity (EOQ)
    # EOQ = sqrt( (2 * D * S) / H )
    annual_demand = np.maximum(df['avg_daily_demand'] * 365, 10.0)
    annual_holding_cost_per_unit = np.maximum(df['avg_price'] * holding_cost_annual_rate, 0.20)
    
    df['eoq'] = np.ceil(np.sqrt((2 * annual_demand * ordering_cost_per_order) / annual_holding_cost_per_unit)).astype(int)
    
    # 4. Simulate current on-hand warehouse inventory to demonstrate operational recommendations
    np.random.seed(42)
    # Simulate realistic inventory levels centered around ROP
    simulated_stock_ratio = np.random.uniform(0.3, 2.5, size=len(df))
    df['current_stock'] = np.ceil(df['reorder_point'] * simulated_stock_ratio).astype(int)
    
    # 5. Inventory Health Classification
    def classify_status(row):
        curr = row['current_stock']
        ss = row['safety_stock']
        rop = row['reorder_point']
        if curr < ss:
            return "Critical Risk"
        elif curr <= rop:
            return "Reorder Triggered"
        elif curr <= 2 * rop:
            return "Optimal"
        else:
            return "Overstocked"
            
    df['stock_status'] = df.apply(classify_status, axis=1)
    
    # 6. Actionable recommendations
    def recommend_action(row):
        status = row['stock_status']
        if status in ["Critical Risk", "Reorder Triggered"]:
            order_qty = max(row['eoq'], row['reorder_point'] - row['current_stock'] + row['safety_stock'])
            return f"Order {int(order_qty):,} units immediately"
        elif status == "Optimal":
            return "Maintain current stock levels"
        else:
            excess = row['current_stock'] - (2 * row['reorder_point'])
            return f"Overstock alert: Pause purchase orders (Excess: {int(excess):,} units)"
            
    df['recommended_action'] = df.apply(recommend_action, axis=1)
    
    # 7. Financial impact calculation
    overstock_items = df[df['stock_status'] == "Overstocked"]
    excess_capital_tied = ((overstock_items['current_stock'] - overstock_items['reorder_point'] * 1.5) * overstock_items['avg_price']).sum()
    
    crit_items = df[df['stock_status'] == "Critical Risk"]
    stockout_risk_exposure = (crit_items['reorder_point'] * crit_items['avg_price']).sum()
    
    out_path = os.path.join("data", "processed", "inventory_recommendations.csv")
    df.to_csv(out_path, index=False)
    
    print(f"\nInventory optimization computed for {len(df):,} products")
    print("--- Stock Status Distribution ---")
    print(df['stock_status'].value_counts())
    print(f"\nEstimated Capital Tied in Overstock: £{excess_capital_tied:,.2f}")
    print(f"Revenue at Risk from Stockouts: £{stockout_risk_exposure:,.2f}")
    print(f"Recommendations saved to {out_path} [OK]")
    print("==================================================")

if __name__ == "__main__":
    run_inventory_optimization()

