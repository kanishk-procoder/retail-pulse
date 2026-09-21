import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Model Benchmark Leaderboard | RetailPulse", page_icon="🏆", layout="wide")

st.title("🏆 AI Model Benchmark Leaderboard & Registry")
st.markdown("Head-to-head performance audit across all **18 AI models** developed for segmentation, forecasting, and churn.")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
kpi_path = os.path.join(data_dir, "master_leaderboards.json")

if os.path.exists(kpi_path):
    with open(kpi_path) as f:
        master = json.load(f)
        
    tab1, tab2, tab3 = st.tabs(["📈 Demand Forecasting (7 Models)", "⚠️ Churn Prediction (7 Models)", "👥 Customer Segmentation (4 Models)"])
    
    # -------------------------------------------------------------
    # TAB 1: FORECASTING
    # -------------------------------------------------------------
    with tab1:
        st.subheader("1. Demand Forecasting Model Benchmarking")
        fore_df = pd.DataFrame(master.get("forecasting", [])).sort_values("MAPE").reset_index(drop=True)
        fore_df['Rank'] = range(1, len(fore_df) + 1)
        fore_df['Status'] = fore_df['Rank'].apply(lambda r: "🥇 Champion Selected" if r == 1 else "Evaluated Alternative")
        
        st.dataframe(
            fore_df[['Rank', 'Model', 'MAPE', 'RMSE', 'MAE', 'R2', 'Status']],
            column_config={
                "MAPE": st.column_config.NumberColumn("MAPE (%)", format="%.2f%%"),
                "RMSE": st.column_config.NumberColumn("RMSE (£)", format="£%.2f"),
                "MAE": st.column_config.NumberColumn("MAE (£)", format="£%.2f"),
                "R2": st.column_config.NumberColumn("R² Score", format="%.4f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fig_mape = px.bar(
                fore_df,
                x='Model',
                y='MAPE',
                color='MAPE',
                color_continuous_scale='Teal_r',
                title="Forecast Error: MAPE Comparison (Lower is Better)",
                labels={'MAPE': 'MAPE (%)'}
            )
            fig_mape.add_hline(y=12.0, line_dash="dash", line_color="green", annotation_text="Industry Target (12%)")
            fig_mape.update_layout(height=340)
            st.plotly_chart(fig_mape, use_container_width=True)
            
        with col_f2:
            fig_r2 = px.bar(
                fore_df,
                x='Model',
                y='R2',
                color='R2',
                color_continuous_scale='Blues',
                title="Goodness-of-Fit: R² Score Comparison (Higher is Better)",
                labels={'R2': 'R² Score'}
            )
            fig_r2.update_layout(height=340)
            st.plotly_chart(fig_r2, use_container_width=True)
            
    # -------------------------------------------------------------
    # TAB 2: CHURN PREDICTION
    # -------------------------------------------------------------
    with tab2:
        st.subheader("2. Customer Churn Classifier Benchmarking")
        churn_df = pd.DataFrame(master.get("churn", [])).sort_values("AUC_ROC", ascending=False).reset_index(drop=True)
        churn_df['Rank'] = range(1, len(churn_df) + 1)
        churn_df['Status'] = churn_df['Rank'].apply(lambda r: "🥇 Champion Selected" if r == 1 else "Evaluated Alternative")
        
        st.dataframe(
            churn_df[['Rank', 'Model', 'AUC_ROC', 'Accuracy', 'Precision', 'Recall', 'F1_Score', 'Precision_Top20', 'Status']],
            column_config={
                "AUC_ROC": st.column_config.NumberColumn("AUC-ROC", format="%.4f"),
                "Accuracy": st.column_config.NumberColumn("Accuracy", format="%.4f"),
                "Precision": st.column_config.NumberColumn("Precision", format="%.4f"),
                "Recall": st.column_config.NumberColumn("Recall", format="%.4f"),
                "F1_Score": st.column_config.NumberColumn("F1-Score", format="%.4f"),
                "Precision_Top20": st.column_config.NumberColumn("Precision @ Top 20%", format="%.4f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_auc = px.bar(
                churn_df,
                x='Model',
                y='AUC_ROC',
                color='AUC_ROC',
                color_continuous_scale='Purples',
                title="Discriminative Power: AUC-ROC (Higher is Better)"
            )
            fig_auc.add_hline(y=0.80, line_dash="dash", line_color="orange", annotation_text="Benchmark (0.80)")
            fig_auc.update_layout(height=340)
            st.plotly_chart(fig_auc, use_container_width=True)
            
        with col_c2:
            fig_f1 = px.bar(
                churn_df,
                x='Model',
                y='Precision_Top20',
                color='Precision_Top20',
                color_continuous_scale='Viridis',
                title="Business Metric: Precision @ Top 20% Highest Risk"
            )
            fig_f1.add_hline(y=0.75, line_dash="dash", line_color="green", annotation_text="Target (75%)")
            fig_f1.update_layout(height=340)
            st.plotly_chart(fig_f1, use_container_width=True)
            
    # -------------------------------------------------------------
    # TAB 3: CUSTOMER SEGMENTATION
    # -------------------------------------------------------------
    with tab3:
        st.subheader("3. Unsupervised Clustering Model Benchmarking")
        seg_df = pd.DataFrame(master.get("segmentation", [])).sort_values("Silhouette_Score", ascending=False).reset_index(drop=True)
        seg_df['Rank'] = range(1, len(seg_df) + 1)
        seg_df['Status'] = seg_df['Selected'].apply(lambda s: "🥇 Champion Selected" if s else "Evaluated Alternative")
        
        st.dataframe(
            seg_df[['Rank', 'Model', 'Clusters', 'Silhouette_Score', 'Calinski_Harabasz', 'Davies_Bouldin', 'Interpretability', 'Status']],
            column_config={
                "Silhouette_Score": st.column_config.NumberColumn("Silhouette Score", format="%.4f"),
                "Calinski_Harabasz": st.column_config.NumberColumn("Calinski-Harabasz", format="%.2f"),
                "Davies_Bouldin": st.column_config.NumberColumn("Davies-Bouldin", format="%.4f")
            },
            hide_index=True,
            use_container_width=True
        )
        
        fig_seg = px.bar(
            seg_df,
            x='Model',
            y='Silhouette_Score',
            color='Silhouette_Score',
            color_continuous_scale='Sunset',
            title="Cluster Separation: Silhouette Score (Higher is Better)"
        )
        fig_seg.update_layout(height=340)
        st.plotly_chart(fig_seg, use_container_width=True)

