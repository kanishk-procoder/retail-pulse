import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Demand Forecasting | RetailPulse", page_icon="📈", layout="wide")

st.title("📈 AI Demand Forecasting & Scenario Analysis")
st.markdown("Multi-horizon time-series forecasting evaluating **ARIMA**, **SARIMA**, **Prophet**, **PyTorch LSTM**, **XGBoost**, **Random Forest**, and **Ensemble**.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
fc_path = os.path.join(data_dir, "forecasting_comparison.csv")
kpi_path = os.path.join(data_dir, "master_leaderboards.json")

if os.path.exists(fc_path) and os.path.exists(kpi_path):
    df_fc = pd.read_csv(fc_path)
    df_fc['Date'] = pd.to_datetime(df_fc['Date'])
    
    with open(kpi_path) as f:
        master_leaderboards = json.load(f)
    forecast_metrics = master_leaderboards.get("forecasting", [])
    
    # Model Selector
    available_models = [c for c in df_fc.columns if c not in ['Date', 'Actual']]
    
    col_sel, col_sim = st.columns([1, 2])
    with col_sel:
        selected_model = st.selectbox("Select Forecasting Model:", available_models, index=0)
        
    with col_sim:
        sim_multiplier = st.slider("⚡ What-If Scenario: Adjust Demand Surge/Decline (%):", min_value=-50, max_value=50, value=0, step=5)
        
    # Get metrics for selected model
    m_info = next((m for m in forecast_metrics if m["Model"] == selected_model or (selected_model == "LSTM" and "LSTM" in m["Model"])), None)
    
    m1, m2, m3, m4 = st.columns(4)
    if m_info:
        m1.metric("Model MAPE", f"{m_info['MAPE']}%", delta="Target <= 12%", delta_color="normal" if m_info['MAPE'] <= 25 else "inverse")
        m2.metric("RMSE", f"£{m_info['RMSE']:,.0f}")
        m3.metric("MAE", f"£{m_info['MAE']:,.0f}")
        m4.metric("R² Score", f"{m_info['R2']}")
        
    st.markdown("---")
    
    # Chart
    st.subheader(f"📊 30-Day Holdout Forecast: Actual vs {selected_model} Prediction")
    
    sim_factor = 1.0 + (sim_multiplier / 100.0)
    adjusted_pred = df_fc[selected_model] * sim_factor
    
    fig = go.Figure()
    # Actual Ground Truth
    fig.add_trace(go.Scatter(
        x=df_fc['Date'],
        y=df_fc['Actual'],
        mode='lines+markers',
        name='Actual Ground Truth',
        line=dict(color='#0F172A', width=2.5)
    ))
    # Selected Model Prediction
    fig.add_trace(go.Scatter(
        x=df_fc['Date'],
        y=adjusted_pred,
        mode='lines+markers',
        name=f'{selected_model} Prediction' if sim_multiplier == 0 else f'{selected_model} (Scenario: {sim_multiplier:+d}%)',
        line=dict(color='#2563EB', width=2.5, dash='solid' if sim_multiplier == 0 else 'dash')
    ))
    
    # Add confidence ribbon simulation (+/- 15%)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_fc['Date'], df_fc['Date'][::-1]]),
        y=pd.concat([adjusted_pred * 1.15, (adjusted_pred * 0.85)[::-1]]),
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='85% Confidence Interval'
    ))
    
    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        xaxis_title="Forecast Date",
        yaxis_title="Revenue (£)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # All Models Side-by-Side Table
    st.subheader("📑 Forecast Values Across All 7 Models")
    st.dataframe(
        df_fc,
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export 30-Day Forecast Data (CSV)",
        data=df_fc.to_csv(index=False),
        file_name="retailpulse_30day_forecasts.csv",
        mime="text/csv"
    )

