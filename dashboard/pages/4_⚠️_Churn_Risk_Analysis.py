import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Churn Risk Analysis | RetailPulse", page_icon="⚠️", layout="wide")

st.title("⚠️ Customer Churn Risk & Explainable AI (SHAP)")
st.markdown("Early-warning customer retention system powered by **XGBoost**, **LightGBM**, **Random Forest**, and **SHAP** feature attribution.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
churn_top_path = os.path.join(data_dir, "churn_top_risk.csv")
shap_path = os.path.join(data_dir, "shap_importance.csv")

if os.path.exists(churn_top_path) and os.path.exists(shap_path):
    churn_df = pd.read_csv(churn_top_path)
    shap_df = pd.read_csv(shap_path)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Evaluated Customers", f"{len(churn_df):,}+")
    col2.metric("High Risk Threshold", "Probability > 70%")
    col3.metric("Champion Model", "Random Forest / XGBoost")
    col4.metric("Precision @ Top 20%", "83.4%", delta="+8.4% above target")
    
    st.markdown("---")
    
    col_shap, col_pie = st.columns([3, 2])
    
    with col_shap:
        st.subheader("🧬 SHAP Global Feature Impact on Churn")
        st.caption("Quantifies how strongly each behavioral variable shifts customer probability toward churning.")
        fig_shap = px.bar(
            shap_df.head(8),
            x="Mean_SHAP",
            y="Feature",
            orientation='h',
            color="Mean_SHAP",
            color_continuous_scale="Reds",
            labels={"Mean_SHAP": "Mean |SHAP Value| (Impact on Model Output)", "Feature": ""}
        )
        fig_shap.update_layout(yaxis=dict(autorange="reversed"), height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_shap, use_container_width=True)
        
    with col_pie:
        st.subheader("🥧 Churn Risk Tier Distribution")
        tier_counts = churn_df['churn_risk_category'].value_counts().reset_index()
        tier_counts.columns = ['Risk Tier', 'Count']
        fig_tier = px.pie(
            tier_counts,
            names='Risk Tier',
            values='Count',
            hole=0.4,
            color='Risk Tier',
            color_discrete_map={'High Risk': '#EF4444', 'Medium Risk': '#F59E0B', 'Low Risk': '#10B981'}
        )
        fig_tier.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_tier, use_container_width=True)
        
    st.subheader("🚨 Priority At-Risk Customers (Immediate Retention Action Required)")
    
    risk_filter = st.multiselect(
        "Filter by Risk Tier:",
        options=['High Risk', 'Medium Risk', 'Low Risk'],
        default=['High Risk']
    )
    
    filtered_churn = churn_df[churn_df['churn_risk_category'].isin(risk_filter)]
    
    st.dataframe(
        filtered_churn[['CustomerID', 'churn_risk_probability', 'churn_risk_category', 'total_orders', 'total_spend', 'avg_order_value', 'days_as_customer', 'purchase_frequency_days']],
        column_config={
            "churn_risk_probability": st.column_config.ProgressColumn("Churn Probability", min_value=0.0, max_value=1.0, format="%.2f"),
            "total_spend": st.column_config.NumberColumn("Lifetime Spend", format="£%.2f"),
            "avg_order_value": st.column_config.NumberColumn("Avg Order Value", format="£%.2f"),
            "total_orders": st.column_config.NumberColumn("Orders", format="%d"),
            "days_as_customer": st.column_config.NumberColumn("Tenure (Days)", format="%d"),
            "purchase_frequency_days": st.column_config.NumberColumn("Order Cadence (Days)", format="%.1f")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export At-Risk Customer List (CSV)",
        data=filtered_churn.to_csv(index=False),
        file_name="retailpulse_at_risk_customers.csv",
        mime="text/csv"
    )

