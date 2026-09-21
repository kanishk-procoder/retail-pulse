import os
import pandas as pd
import numpy as np
from datetime import datetime

def run_preprocessing():
    print("==================================================")
    print("RETAILPULSE: STEP 1 - DATA LOADING & PREPROCESSING")
    print("==================================================")
    
    raw_path = os.path.join("data", "raw", "online_retail_II.xlsx")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}")
        
    print(f"Reading {raw_path} (this may take a minute for 1M+ rows)...")
    # Read both sheets
    df1 = pd.read_excel(raw_path, sheet_name="Year 2009-2010")
    print(f"Sheet 1 (2009-2010) loaded: {df1.shape[0]:,} rows")
    
    df2 = pd.read_excel(raw_path, sheet_name="Year 2010-2011")
    print(f"Sheet 2 (2010-2011) loaded: {df2.shape[0]:,} rows")
    
    # Standardize column names
    col_map = {
        'Invoice': 'Invoice',
        'StockCode': 'StockCode',
        'Description': 'Description',
        'Quantity': 'Quantity',
        'InvoiceDate': 'InvoiceDate',
        'Price': 'Price',
        'Customer ID': 'CustomerID',
        'Country': 'Country'
    }
    df1 = df1.rename(columns=col_map)
    df2 = df2.rename(columns=col_map)
    
    df = pd.concat([df1, df2], ignore_index=True)
    initial_rows = len(df)
    print(f"\nTotal raw combined rows: {initial_rows:,}")
    
    audit = [{"Step": "Raw Ingestion", "Rows_Remaining": initial_rows, "Rows_Removed": 0, "Pct_Removed": 0.0}]
    
    # 1. Filter out cancellations (Invoice starting with 'C')
    is_cancelled = df['Invoice'].astype(str).str.startswith('C')
    cancelled_count = is_cancelled.sum()
    df = df[~is_cancelled]
    audit.append({
        "Step": "Remove Cancellations ('C')",
        "Rows_Remaining": len(df),
        "Rows_Removed": cancelled_count,
        "Pct_Removed": round(cancelled_count / initial_rows * 100, 2)
    })
    
    # 2. Filter positive Quantity and Price
    valid_qty_price = (df['Quantity'] > 0) & (df['Price'] > 0)
    invalid_count = (~valid_qty_price).sum()
    df = df[valid_qty_price]
    audit.append({
        "Step": "Filter Quantity > 0 and Price > 0",
        "Rows_Remaining": len(df),
        "Rows_Removed": invalid_count,
        "Pct_Removed": round(invalid_count / initial_rows * 100, 2)
    })
    
    # 3. Handle missing CustomerID
    missing_cust = df['CustomerID'].isnull().sum()
    df = df[df['CustomerID'].notnull()]
    df['CustomerID'] = df['CustomerID'].astype(int)
    audit.append({
        "Step": "Remove Null Customer IDs",
        "Rows_Remaining": len(df),
        "Rows_Removed": missing_cust,
        "Pct_Removed": round(missing_cust / initial_rows * 100, 2)
    })
    
    # 4. Remove duplicate rows
    dups = df.duplicated().sum()
    df = df.drop_duplicates()
    audit.append({
        "Step": "Remove Duplicate Rows",
        "Rows_Remaining": len(df),
        "Rows_Removed": dups,
        "Pct_Removed": round(dups / initial_rows * 100, 2)
    })
    
    # 5. Create TotalAmount & Date Features
    df['TotalAmount'] = (df['Quantity'] * df['Price']).round(2)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Date'] = df['InvoiceDate'].dt.date
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month
    df['Day'] = df['InvoiceDate'].dt.day
    df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
    df['Hour'] = df['InvoiceDate'].dt.hour
    df['is_weekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
    
    # 6. Winsorize extreme outliers at 99.9th percentile for clean modeling
    q_cap = df['Quantity'].quantile(0.999)
    p_cap = df['Price'].quantile(0.999)
    df['Quantity_Capped'] = df['Quantity'].clip(upper=q_cap)
    df['Price_Capped'] = df['Price'].clip(upper=p_cap)
    df['TotalAmount_Capped'] = (df['Quantity_Capped'] * df['Price_Capped']).round(2)
    
    # Ensure string types for mixed-type columns
    df['Invoice'] = df['Invoice'].astype(str)
    df['StockCode'] = df['StockCode'].astype(str)
    df['Description'] = df['Description'].fillna('').astype(str)
    df['Country'] = df['Country'].fillna('Unknown').astype(str)
    df['Date'] = df['Date'].astype(str)
    
    # Save cleaned outputs
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    out_csv = os.path.join("data", "processed", "cleaned_transactions.csv")
    out_parquet = os.path.join("data", "processed", "cleaned_transactions.parquet")
    
    print("\nSaving cleaned transactions to CSV & Parquet...")
    df.to_parquet(out_parquet, index=False)
    # Also save a standard CSV (first 250,000 rows or full for quick sampling if needed)
    df.to_csv(out_csv, index=False)
    
    print("\n=== Data Cleaning Audit Summary ===")
    audit_df = pd.DataFrame(audit)
    print(audit_df.to_string(index=False))
    
    print(f"\nFinal cleaned dataset: {len(df):,} transactions from {df['CustomerID'].nunique():,} unique customers")
    print(f"Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
    print(f"Saved: {out_csv} and {out_parquet} [OK]\n")
    return df

if __name__ == "__main__":
    run_preprocessing()
