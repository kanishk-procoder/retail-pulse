import os
import pandas as pd
import numpy as np
from datetime import timedelta

def run_feature_engineering():
    print("==================================================")
    print("RETAILPULSE: STEP 2 - FEATURE ENGINEERING")
    print("==================================================")
    
    clean_path = os.path.join("data", "processed", "cleaned_transactions.parquet")
    if not os.path.exists(clean_path):
        clean_path = os.path.join("data", "processed", "cleaned_transactions.csv")
    
    print(f"Loading cleaned data from {clean_path}...")
    if clean_path.endswith('.parquet'):
        df = pd.read_parquet(clean_path)
    else:
        df = pd.read_csv(clean_path)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # -------------------------------------------------------------
    # 1. RFM FEATURES
    # -------------------------------------------------------------
    print("\n1. Calculating RFM Metrics...")
    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'nunique',
        'TotalAmount': 'sum'
    }).reset_index()
    
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    rfm['Monetary'] = rfm['Monetary'].round(2)
    
    # Quantile scoring (1-5)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    def assign_segment(row):
        r, f = row['R_Score'], row['F_Score']
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "Promising / New"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Lost / Inactive"
        else:
            return "Needs Attention"
            
    rfm['RFM_Segment'] = rfm.apply(assign_segment, axis=1)
    
    rfm_path = os.path.join("data", "processed", "rfm_features.csv")
    rfm.to_csv(rfm_path, index=False)
    print(f"   RFM features created for {len(rfm):,} customers -> {rfm_path}")
    print("   Segment distribution:")
    print(rfm['RFM_Segment'].value_counts())
    
    # -------------------------------------------------------------
    # 2. TIME-SERIES DAILY FEATURES (FOR DEMAND FORECASTING)
    # -------------------------------------------------------------
    print("\n2. Engineering Time-Series Forecasting Features...")
    daily = df.groupby('Date').agg({
        'TotalAmount': 'sum',
        'Quantity': 'sum',
        'Invoice': 'nunique',
        'CustomerID': 'nunique'
    }).reset_index()
    daily.columns = ['Date', 'Revenue', 'TotalQuantity', 'Transactions', 'UniqueCustomers']
    
    # Ensure continuous calendar date range
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.sort_values('Date')
    full_idx = pd.date_range(start=daily['Date'].min(), end=daily['Date'].max(), freq='D')
    daily = daily.set_index('Date').reindex(full_idx).fillna(0).reset_index()
    daily.columns = ['Date', 'Revenue', 'TotalQuantity', 'Transactions', 'UniqueCustomers']
    
    # Lag features
    for lag in [1, 2, 3, 7, 14, 21, 30]:
        daily[f'lag_{lag}'] = daily['Revenue'].shift(lag)
        
    # Rolling statistics
    daily['rolling_mean_7'] = daily['Revenue'].shift(1).rolling(window=7).mean()
    daily['rolling_std_7'] = daily['Revenue'].shift(1).rolling(window=7).std()
    daily['rolling_mean_14'] = daily['Revenue'].shift(1).rolling(window=14).mean()
    daily['rolling_mean_30'] = daily['Revenue'].shift(1).rolling(window=30).mean()
    daily['rolling_std_30'] = daily['Revenue'].shift(1).rolling(window=30).std()
    
    # Calendar & Cyclical features
    daily['day_of_week'] = daily['Date'].dt.dayofweek
    daily['day_of_month'] = daily['Date'].dt.day
    daily['month'] = daily['Date'].dt.month
    daily['quarter'] = daily['Date'].dt.quarter
    daily['is_weekend'] = daily['day_of_week'].isin([5, 6]).astype(int)
    daily['sin_dow'] = np.sin(2 * np.pi * daily['day_of_week'] / 7)
    daily['cos_dow'] = np.cos(2 * np.pi * daily['day_of_week'] / 7)
    daily['sin_month'] = np.sin(2 * np.pi * daily['month'] / 12)
    daily['cos_month'] = np.cos(2 * np.pi * daily['month'] / 12)
    
    # Drop warm-up NaN rows caused by 30-day rolling/lag
    ts_clean = daily.dropna().copy()
    ts_path = os.path.join("data", "processed", "timeseries_features.csv")
    ts_clean.to_csv(ts_path, index=False)
    print(f"   Daily time-series features: {len(ts_clean)} days -> {ts_path}")
    
    # -------------------------------------------------------------
    # 3. CHURN PREDICTION FEATURES
    # -------------------------------------------------------------
    print("\n3. Engineering Customer Churn Features...")
    max_date = df['InvoiceDate'].max()
    churn_threshold = max_date - timedelta(days=90)
    print(f"   Dataset max date: {max_date}")
    print(f"   Churn threshold (90 days prior): {churn_threshold}")
    
    # Customer level aggregates
    cust_agg = df.groupby('CustomerID').agg({
        'InvoiceDate': ['min', 'max', 'count'],
        'Invoice': 'nunique',
        'Quantity': ['sum', 'mean'],
        'TotalAmount': ['sum', 'mean'],
        'StockCode': 'nunique',
        'is_weekend': 'mean'
    })
    cust_agg.columns = [
        'first_purchase', 'last_purchase', 'total_items_bought',
        'total_orders', 'total_quantity', 'avg_quantity_per_line',
        'total_spend', 'avg_order_value', 'unique_products_bought',
        'weekend_purchase_ratio'
    ]
    cust_agg = cust_agg.reset_index()
    
    # Churn definition: Customer whose last purchase was BEFORE the churn threshold (>= 90 days of inactivity)
    cust_agg['is_churned'] = (cust_agg['last_purchase'] < churn_threshold).astype(int)
    
    # Behavioral features
    cust_agg['days_as_customer'] = (cust_agg['last_purchase'] - cust_agg['first_purchase']).dt.days + 1
    cust_agg['recency_days'] = (snapshot_date - cust_agg['last_purchase']).dt.days
    cust_agg['purchase_frequency_days'] = (cust_agg['days_as_customer'] / cust_agg['total_orders']).round(1)
    cust_agg['recency_frequency_ratio'] = (cust_agg['recency_days'] / (cust_agg['total_orders'] + 1)).round(2)
    
    # Merge with RFM scores
    cust_features = cust_agg.merge(rfm[['CustomerID', 'R_Score', 'F_Score', 'M_Score', 'RFM_Segment']], on='CustomerID', how='left')
    
    churn_path = os.path.join("data", "processed", "churn_features.csv")
    cust_features.to_csv(churn_path, index=False)
    churn_rate = cust_features['is_churned'].mean() * 100
    print(f"   Customer Churn dataset: {len(cust_features):,} customers -> {churn_path}")
    print(f"   Churn class balance: Active = {(100 - churn_rate):.1f}%, Churned = {churn_rate:.1f}%")
    
    # -------------------------------------------------------------
    # 4. PRODUCT-LEVEL FEATURES (FOR INVENTORY OPTIMIZATION)
    # -------------------------------------------------------------
    print("\n4. Engineering Product-Level Inventory Features...")
    prod_agg = df.groupby(['StockCode', 'Description']).agg({
        'Quantity': ['sum', 'count', 'std'],
        'TotalAmount': 'sum',
        'Price': 'mean',
        'CustomerID': 'nunique'
    }).reset_index()
    
    prod_agg.columns = ['StockCode', 'Description', 'total_units_sold', 'transaction_count', 'demand_std', 'total_revenue', 'avg_price', 'unique_customers']
    prod_agg['demand_std'] = prod_agg['demand_std'].fillna(1.0)
    
    total_days = (df['InvoiceDate'].max() - df['InvoiceDate'].min()).days
    prod_agg['avg_daily_demand'] = (prod_agg['total_units_sold'] / total_days).round(2)
    
    # Filter to meaningful retail items
    top_products = prod_agg[prod_agg['total_units_sold'] > 50].sort_values('total_revenue', ascending=False).reset_index(drop=True)
    prod_path = os.path.join("data", "processed", "product_features.csv")
    top_products.to_csv(prod_path, index=False)
    print(f"   Product Inventory dataset: {len(top_products):,} active products -> {prod_path}")
    
    print("\n==================================================")
    print("FEATURE ENGINEERING COMPLETE - ALL DATASETS READY")
    print("==================================================")

if __name__ == "__main__":
    run_feature_engineering()

