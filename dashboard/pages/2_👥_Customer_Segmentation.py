import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Customer Segmentation | RetailPulse", page_icon="👥", layout="wide")

st.title("👥 AI Customer Segmentation & RFM Analytics")
st.markdown("Cluster evaluation and behavioral segmentation comparing **K-Means**, **DBSCAN**, **Agglomerative**, and **Gaussian Mixture Models**.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
seg_summary_path = os.path.join(data_dir, "segmentation_summary.csv")
sample_path = os.path.join(data_dir, "customer_segments_sample.csv")

if os.path.exists(seg_summary_path):
    summary_df = pd.read_csv(seg_summary_path)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Segment Financial Contribution & Size")
        fig_bar = px.bar(
            summary_df,
            x="Segment",
            y="TotalRevenue",
            color="Segment",
            text_auto='.2s',
            labels={"TotalRevenue": "Total Revenue (£)"},
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_bar.update_layout(height=350, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        st.subheader("🍩 Customer Share by Segment")
        fig_pie = px.pie(
            summary_df,
            names="Segment",
            values="CustomerCount",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.subheader("📋 Segment Profiles & Actionable Retention Strategies")
    
    # Custom display columns
    display_df = summary_df.copy()
    display_df['Strategy'] = display_df['Segment'].map({
        "VIP Champions": "Reward with exclusive VIP perks, early access, and loyalty multipliers.",
        "Loyal Customers": "Upsell premium categories and proactive engagement to sustain frequency.",
        "New Active": "Welcome sequence, onboarding offers, and second-order incentives.",
        "At-Risk Churn": "Win-back discounts, survey feedback, and targeted retention emails.",
        "Hibernating Low-Value": "Low-cost re-engagement or automated discount drip campaigns."
    }).fillna("Standard engagement campaign")
    
    st.dataframe(
        display_df[['Segment', 'CustomerCount', 'AvgRecency', 'AvgFrequency', 'AvgMonetary', 'TotalRevenue', 'RevenueShare', 'Strategy']],
        column_config={
            "CustomerCount": st.column_config.NumberColumn("Customers", format="%d"),
            "AvgRecency": st.column_config.NumberColumn("Avg Recency (Days)", format="%.1f"),
            "AvgFrequency": st.column_config.NumberColumn("Avg Orders", format="%.1f"),
            "AvgMonetary": st.column_config.NumberColumn("Avg Spend", format="£%.2f"),
            "TotalRevenue": st.column_config.NumberColumn("Total Revenue", format="£%.2f"),
            "RevenueShare": st.column_config.NumberColumn("Revenue Share", format="%.1f%%")
        },
        hide_index=True,
        use_container_width=True
    )

# 3D Interactive Scatter Plot
if os.path.exists(sample_path):
    st.markdown("---")
    st.subheader("🌐 3D Interactive RFM Feature Space (Log Scaled)")
    sample_df = pd.read_csv(sample_path)
    
    fig_3d = px.scatter_3d(
        sample_df,
        x="Recency",
        y="Frequency",
        z="Monetary",
        color="Final_Segment",
        hover_data=["CustomerID", "RFM_Segment"],
        log_y=True,
        log_z=True,
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_3d.update_layout(
        height=550,
        margin=dict(l=10, r=10, t=20, b=10),
        scene=dict(
            xaxis_title="Recency (Days)",
            yaxis_title="Frequency (Orders - Log)",
            zaxis_title="Monetary (£ - Log)"
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# Customer Lookup Section
st.markdown("---")
st.subheader("🔍 Individual Customer Segmentation Lookup")
col_s1, col_s2 = st.columns([1, 2])

with col_s1:
    cust_id_input = st.number_input("Enter Customer ID:", min_value=10000, max_value=99999, value=12347, step=1)
    
full_seg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", "customer_segments.csv")
if os.path.exists(full_seg_path):
    full_seg = pd.read_csv(full_seg_path)
    cust_record = full_seg[full_seg['CustomerID'] == cust_id_input]
    
    with col_s2:
        if len(cust_record) > 0:
            row = cust_record.iloc[0]
            st.success(f"**Customer {cust_id_input} identified:** Assigned to **{row['Final_Segment']}** ({row['RFM_Segment']})")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Recency", f"{int(row['Recency'])} days")
            m2.metric("Orders (Freq)", f"{int(row['Frequency'])}")
            m3.metric("Total Spend", f"£{row['Monetary']:,.2f}")
            m4.metric("RFM Score", f"{row['RFM_Score']}")
        else:
            st.warning(f"Customer ID {cust_id_input} not found in database.")

