import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Inventory Optimization | RetailPulse", page_icon="📦", layout="wide")

st.title("📦 Prescriptive Inventory Optimization & Reorder Engine")
st.markdown("Demand-driven stock replenishment: **Safety Stock**, **Reorder Points (ROP)**, and **Economic Order Quantities (EOQ)** preventing stockouts while minimizing holding costs.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
inv_path = os.path.join(data_dir, "inventory_alerts.csv")
full_inv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", "inventory_recommendations.csv")

if os.path.exists(full_inv_path):
    inv_df = pd.read_csv(full_inv_path)
    
    # KPIs
    crit_count = (inv_df['stock_status'] == "Critical Risk").sum()
    reorder_count = (inv_df['stock_status'] == "Reorder Triggered").sum()
    optimal_count = (inv_df['stock_status'] == "Optimal").sum()
    overstock_count = (inv_df['stock_status'] == "Overstocked").sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 Critical Stockout Risk", f"{crit_count:,}", delta="Below Safety Stock", delta_color="inverse")
    col2.metric("🟡 Reorder Triggered", f"{reorder_count:,}", delta="Below ROP", delta_color="inverse")
    col3.metric("🟢 Optimal Health", f"{optimal_count:,}")
    col4.metric("🔵 Overstocked", f"{overstock_count:,}", delta="Excess Capital Tied", delta_color="off")
    
    st.markdown("---")
    
    # Interactive Service Level Simulation
    st.subheader("⚙️ Dynamic Service Level Policy Tuning")
    service_level = st.select_slider(
        "Target Service Level (Z-Factor): Higher protection against stockouts requires higher safety buffer.",
        options=[90, 92, 95, 98, 99],
        value=95,
        format_func=lambda x: f"{x}% Target Availability"
    )
    
    z_map = {90: 1.28, 92: 1.41, 95: 1.65, 98: 2.05, 99: 2.33}
    curr_z = z_map[service_level]
    st.caption(f"Active Z-score: **{curr_z}** | Standard Supplier Lead Time: **7 Days**")
    
    # Stock Status Distribution & Financial Exposure
    col_pie, col_bar = st.columns([2, 3])
    
    with col_pie:
        st.subheader("Inventory Health Breakdown")
        status_df = inv_df['stock_status'].value_counts().reset_index()
        status_df.columns = ['Status', 'Count']
        fig_pie = px.pie(
            status_df,
            names='Status',
            values='Count',
            hole=0.45,
            color='Status',
            color_discrete_map={
                'Critical Risk': '#DC2626',
                'Reorder Triggered': '#F59E0B',
                'Optimal': '#10B981',
                'Overstocked': '#3B82F6'
            }
        )
        fig_pie.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_bar:
        st.subheader("Working Capital Breakdown by Category")
        capital_df = inv_df.groupby('stock_status').agg({
            'current_stock': lambda x: (x * inv_df.loc[x.index, 'avg_price']).sum()
        }).reset_index()
        capital_df.columns = ['Status', 'TotalCapital']
        fig_bar = px.bar(
            capital_df,
            x='Status',
            y='TotalCapital',
            color='Status',
            text_auto='.2s',
            labels={'TotalCapital': 'Inventory Value (£)', 'Status': ''},
            color_discrete_map={
                'Critical Risk': '#DC2626',
                'Reorder Triggered': '#F59E0B',
                'Optimal': '#10B981',
                'Overstocked': '#3B82F6'
            }
        )
        fig_bar.update_layout(height=320, showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.subheader("🚨 Product Reorder Action Console")
    
    status_filter = st.multiselect(
        "Filter Items by Inventory Status:",
        options=['Critical Risk', 'Reorder Triggered', 'Optimal', 'Overstocked'],
        default=['Critical Risk', 'Reorder Triggered']
    )
    
    filtered_items = inv_df[inv_df['stock_status'].isin(status_filter)]
    
    st.dataframe(
        filtered_items[['StockCode', 'Description', 'avg_price', 'avg_daily_demand', 'safety_stock', 'reorder_point', 'current_stock', 'eoq', 'stock_status', 'recommended_action']],
        column_config={
            "avg_price": st.column_config.NumberColumn("Unit Price", format="£%.2f"),
            "avg_daily_demand": st.column_config.NumberColumn("Daily Demand", format="%.1f"),
            "safety_stock": st.column_config.NumberColumn("Safety Stock", format="%d"),
            "reorder_point": st.column_config.NumberColumn("ROP", format="%d"),
            "current_stock": st.column_config.NumberColumn("On-Hand Stock", format="%d"),
            "eoq": st.column_config.NumberColumn("EOQ Batch", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Replenishment Purchase Orders (CSV)",
        data=filtered_items.to_csv(index=False),
        file_name="retailpulse_purchase_orders.csv",
        mime="text/csv"
    )

