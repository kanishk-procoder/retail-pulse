import streamlit as pd_st
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(
    page_title="RetailPulse | AI Customer Analytics & Demand Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Load KPIs
data_dir = os.path.join(os.path.dirname(__file__), "data")
kpi_path = os.path.join(data_dir, "kpis.json")

if os.path.exists(kpi_path):
    with open(kpi_path, "r") as f:
        kpis = json.load(f)
else:
    kpis = {}

st.markdown('<div class="main-title">📊 RetailPulse AI Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">End-to-End Retail Intelligence: Demand Forecasting • Customer Segmentation • Churn Prediction • Inventory Optimization</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/shopping-cart.png", width=120)
    st.title("RetailPulse v2.0")
    st.markdown("**Industry Edition (March 2026)**")
    st.info("Zidio Development Internship Project")
    st.markdown("---")
    st.markdown("### 📌 Navigation")
    st.markdown("""
    - **Home / Overview**
    - **2. Customer Segmentation**
    - **3. Demand Forecasting**
    - **4. Churn Risk Analysis**
    - **5. Inventory Optimization**
    - **6. Model Leaderboard**
    """)
    st.markdown("---")
    st.caption("Developed with Python, Scikit-learn, PyTorch, XGBoost, Prophet & Streamlit.")

# Top Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">£{:,.0f}</div>
    </div>
    """.format(kpis.get("total_revenue", 0)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Customers</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(kpis.get("total_customers", 0)), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Avg Order Value</div>
        <div class="metric-value">£{:.2f}</div>
    </div>
    """.format(kpis.get("average_order_value", 0)), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Forecaster MAPE</div>
        <div class="metric-value">{:.1f}%</div>
    </div>
    """.format(kpis.get("best_forecaster_mape", 0)), unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Stockout Risk Items</div>
        <div class="metric-value" style="color: #DC2626;">{:,}</div>
    </div>
    """.format(kpis.get("critical_inventory_items", 0)), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sales Trends and Country Breakdown
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📈 Historical Sales Trend (2009 - 2011)")
    daily_path = os.path.join(data_dir, "daily_sales.csv")
    if os.path.exists(daily_path):
        daily_df = pd.read_csv(daily_path)
        daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        
        # Add 7-day rolling mean
        daily_df['7D_Rolling'] = daily_df['Revenue'].rolling(7).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_df['Date'], y=daily_df['Revenue'], mode='lines', name='Daily Revenue', opacity=0.35, line=dict(color='#93C5FD')))
        fig.add_trace(go.Scatter(x=daily_df['Date'], y=daily_df['7D_Rolling'], mode='lines', name='7-Day Rolling Avg', line=dict(color='#1D4ED8', width=2.5)))
        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=340,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🌍 Top Global Markets")
    country_path = os.path.join(data_dir, "country_distribution.csv")
    if os.path.exists(country_path):
        c_df = pd.read_csv(country_path).head(8)
        fig_c = px.bar(
            c_df,
            x="TotalRevenue",
            y="Country",
            orientation='h',
            color="RevenueShare",
            color_continuous_scale="Blues",
            labels={"TotalRevenue": "Revenue (£)", "Country": ""}
        )
        fig_c.update_layout(yaxis=dict(autorange="reversed"), height=340, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_c, use_container_width=True)

# Bottom Section: Top Products & Architecture Blueprint
col_p, col_a = st.columns([3, 2])

with col_p:
    st.subheader("🏆 Best-Selling Products by Revenue")
    top_p_path = os.path.join(data_dir, "top_products.csv")
    if os.path.exists(top_p_path):
        top_df = pd.read_csv(top_p_path).head(8)
        st.dataframe(
            top_df[['StockCode', 'Description', 'QuantitySold', 'TotalRevenue', 'AvgPrice']],
            column_config={
                "TotalRevenue": st.column_config.NumberColumn("Total Revenue", format="£%.2f"),
                "AvgPrice": st.column_config.NumberColumn("Unit Price", format="£%.2f"),
                "QuantitySold": st.column_config.NumberColumn("Units Sold", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )

with col_a:
    st.subheader("⚡ Platform Execution Pillars")
    st.markdown("""
    - **18+ AI Models Evaluated**: K-Means, DBSCAN, GMM, ARIMA, SARIMA, Prophet, PyTorch LSTM, XGBoost, Random Forest, LightGBM, SVM, MLP.
    - **Automated Data Validation**: Missing value resolution, returns ('C') separation, outlier winsorization.
    - **Explainable AI (SHAP)**: Individual customer churn impact scoring.
    - **Financial Optimization**: Safety stock, Reorder Points (ROP) & EOQ minimizing working capital.
    """)
    st.download_button(
        label="📥 Download Executive Summary CSV",
        data=daily_df.to_csv(index=False) if os.path.exists(daily_path) else "",
        file_name="retailpulse_sales_trend.csv",
        mime="text/csv"
    )

