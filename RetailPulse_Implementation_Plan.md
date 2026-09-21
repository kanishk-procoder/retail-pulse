# RetailPulse – Implementation Plan: Dedicated Model Notebooks & Comparative Selection

## Executive Architecture Summary

To ensure maximum modularity, rigorous benchmarking, and production readiness, **every single AI model is isolated into its own dedicated notebook**. Each model notebook independently trains, evaluates, generates diagnostic plots, and saves its metrics and predictions to a standardized tracking registry (`reports/metrics/` and `data/predictions/`). 

Following each modeling stage, a **Dedicated Comparison & Selection Notebook** loads all model runs head-to-head, generates comparative visual benchmarks (e.g., overlaid ROC curves, multi-model forecast plots, cluster metrics), declares the champion model, and promotes it for inventory optimization and live dashboard serving.

---

## 1. Modular Notebook Structure (26 Notebooks Total)

```
notebooks/
│
├── 01_data_pipeline/
│   ├── 01_Data_Loading_and_Preprocessing.ipynb       # Ingestion, cleaning, validation
│   ├── 02_Exploratory_Data_Analysis.ipynb            # 15+ exploratory visualizations & insights
│   └── 03_Feature_Engineering.ipynb                  # RFM, lag/rolling features, churn labels
│
├── 02_customer_segmentation/
│   ├── 04a_Segmentation_KMeans.ipynb                 # K-Means clustering (elbow & silhouette)
│   ├── 04b_Segmentation_DBSCAN.ipynb                 # DBSCAN density clustering & outlier detection
│   ├── 04c_Segmentation_Agglomerative.ipynb          # Hierarchical Agglomerative clustering
│   ├── 04d_Segmentation_GMM.ipynb                    # Gaussian Mixture Model (probabilistic)
│   └── 04e_Segmentation_Comparison_and_Selection.ipynb # Head-to-head evaluation & winner selection
│
├── 03_demand_forecasting/
│   ├── 05a_Forecasting_ARIMA.ipynb                   # Auto-ARIMA baseline
│   ├── 05b_Forecasting_SARIMA.ipynb                  # Seasonal SARIMA with weekly seasonality
│   ├── 05c_Forecasting_Prophet.ipynb                 # Prophet with UK holiday regressors
│   ├── 05d_Forecasting_LSTM.ipynb                    # PyTorch Deep Learning LSTM sequence model
│   ├── 05e_Forecasting_XGBoost.ipynb                 # XGBoost Regressor with lag & rolling features
│   ├── 05f_Forecasting_RandomForest.ipynb            # Random Forest Regressor
│   ├── 05g_Forecasting_Ensemble.ipynb                # Hybrid Prophet + LSTM ensemble
│   └── 05h_Forecasting_Comparison_and_Selection.ipynb # 7-model forecast benchmarking & champion selection
│
├── 04_churn_prediction/
│   ├── 06a_Churn_LogisticRegression.ipynb            # Logistic Regression with interpretable weights
│   ├── 06b_Churn_DecisionTree.ipynb                  # Decision Tree Classifier with tree visualization
│   ├── 06c_Churn_RandomForest.ipynb                  # Random Forest Classifier with feature importance
│   ├── 06d_Churn_XGBoost_SHAP.ipynb                  # XGBoost Classifier with SHAP explainability
│   ├── 06e_Churn_LightGBM.ipynb                      # LightGBM Classifier with leaf-wise boosting
│   ├── 06f_Churn_SVM.ipynb                           # Support Vector Machine (RBF kernel)
│   ├── 06g_Churn_MLP_NeuralNet.ipynb                 # Multi-Layer Perceptron (PyTorch/Sklearn)
│   └── 06h_Churn_Comparison_and_Selection.ipynb     # 7-classifier ROC/PR benchmarking & champion selection
│
└── 05_business_optimization/
    ├── 07_Inventory_Optimization.ipynb               # Safety Stock, ROP, EOQ using champion forecast
    ├── 08_Grand_Model_Evaluation_and_Pipeline.ipynb   # Grand leaderboard & end-to-end pipeline assembly
    ├── 09_Drift_Detection_and_Monitoring.ipynb       # Evidently AI data & concept drift reports
    └── 10_Dashboard_Data_Preparation.ipynb           # Final schema exports for Streamlit dashboard
```

---

## 2. Standardized Model Contract & Inter-Notebook Communication

To make separate notebooks work seamlessly together:

```
┌──────────────────────────────────────┐
│ Individual Model Notebook            │
│ (e.g., 05c_Forecasting_Prophet)     │
│ 1. Train model on processed data     │
│ 2. Compute task-specific metrics     │
│ 3. Save:                             │
│    - models/forecast_prophet.pkl     │
│    - data/predictions/prophet.csv    │
│    - reports/metrics/forecast.json   │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ Comparison & Selection Notebook      │
│ (e.g., 05h_Forecasting_Comparison)   │
│ 1. Load predictions & metrics from   │
│    all 7 model files                 │
│ 2. Overlay plots & metrics table     │
│ 3. Select Winner (lowest MAPE)       │
│ 4. Promote:                          │
│    - models/best_forecaster.pkl      │
│    - data/processed/best_forecast.csv│
└──────────────────────────────────────┘
```

Every model notebook outputs three standard files:
1. **Model Binary**: `models/<task>_<model_name>.pkl`
2. **Out-of-Sample Predictions**: `data/predictions/<task>_<model_name>.csv`
3. **Structured Metrics**: Appended to `reports/metrics/<task>_metrics.json`

---

## 3. Detailed Model Notebook Specifications

### Phase 1: Data Preparation & Exploration
- **01_Data_Loading_and_Preprocessing.ipynb**: Ingests UCI Online Retail II sheets, cleans cancellations ('C'), filters non-positive quantity/prices, handles missing customer IDs, winsorizes outliers (IQR), verifies integrity, and saves `cleaned_transactions.csv`.
- **02_Exploratory_Data_Analysis.ipynb**: Generates 15+ professional visualizations covering revenue trends, country breakdown, peak shopping hours/days, top products/customers, distributions, and correlation matrices.
- **03_Feature_Engineering.ipynb**: Builds RFM matrices, rolling window aggregations, lag features, cyclical calendar signals, and calculates binary 90-day churn labels.

---

### Phase 2: Customer Segmentation (4 Individual Notebooks + 1 Comparison)

#### Individual Model Notebooks:
1. **04a_Segmentation_KMeans.ipynb**:
   - Calculates inertia across $k \in [2, 12]$ (Elbow Method).
   - Computes silhouette scores for each $k$.
   - Fits optimal K-Means model.
   - Generates cluster profile statistics (Mean Recency, Frequency, Monetary).
   - Saves: `models/seg_kmeans.pkl`, `data/predictions/seg_kmeans.csv`.

2. **04b_Segmentation_DBSCAN.ipynb**:
   - Calculates k-distance graph to determine optimal $\varepsilon$ parameter.
   - Tunes `min_samples` parameter.
   - Identifies dense core customer groups and isolates retail outliers/noise points (-1).
   - Saves: `models/seg_dbscan.pkl`, `data/predictions/seg_dbscan.csv`.

3. **04c_Segmentation_Agglomerative.ipynb**:
   - Generates full dendrogram with Ward linkage.
   - Identifies optimal hierarchical cut.
   - Evaluates cluster cohesion.
   - Saves: `models/seg_agglomerative.pkl`, `data/predictions/seg_agglomerative.csv`.

4. **04d_Segmentation_GMM.ipynb**:
   - Evaluates Bayesian Information Criterion (BIC) & Akaike Information Criterion (AIC).
   - Fits Gaussian Mixture Model for probabilistic soft clustering.
   - Outputs assignment certainty probabilities per customer.
   - Saves: `models/seg_gmm.pkl`, `data/predictions/seg_gmm.csv`.

#### Comparison & Selection:
5. **04e_Segmentation_Comparison_and_Selection.ipynb**:
   - Loads cluster assignments and metrics from all 4 models.
   - Compares: Silhouette Score, Calinski-Harabasz Index, Davies-Bouldin Index, and Business Interpretability.
   - Renders 3D Plotly cluster projections and 2D PCA comparison panels.
   - **Selects and promotes**: `models/best_segmentation.pkl` and `data/processed/customer_segments.csv`.

---

### Phase 3: Demand Forecasting (7 Individual Notebooks + 1 Comparison)

*All forecasting models train on identical historical splits and predict the same 30-day holdout test horizon.*

#### Individual Model Notebooks:
1. **05a_Forecasting_ARIMA.ipynb**: `pmdarima.auto_arima` search for optimal $(p, d, q)$. Residual diagnostics and 30-day forecast.
2. **05b_Forecasting_SARIMA.ipynb**: Auto-SARIMA with seasonal period $m=7$ (weekly retail seasonality).
3. **05c_Forecasting_Prophet.ipynb**: Prophet model with weekly/yearly seasonality, trend changepoints, and UK official calendar holidays.
4. **05d_Forecasting_LSTM.ipynb**: PyTorch deep learning architecture (2 LSTM layers, dropout, linear head) with 60-day sequence windows.
5. **05e_Forecasting_XGBoost.ipynb**: XGBoost Regressor leveraging lag features ($t-1, t-7, t-14, t-30$), rolling statistics, and calendar cyclical features.
6. **05f_Forecasting_RandomForest.ipynb**: Random Forest Regressor trained on feature-engineered tabular time series.
7. **05g_Forecasting_Ensemble.ipynb**: Optimal weighted combination and Ridge stacking of Prophet and LSTM predictions.

#### Comparison & Selection:
8. **05h_Forecasting_Comparison_and_Selection.ipynb**:
   - Benchmarks all 7 models against MAPE (target $\le 12\%$), RMSE, MAE, and $R^2$.
   - Overlays all 7 forecast curves against actual ground truth in a unified high-resolution chart.
   - Performs residual distribution and autocorrelation checks for the top models.
   - **Selects and promotes**: `models/best_forecaster.pkl`.

---

### Phase 4: Churn Prediction (7 Individual Notebooks + 1 Comparison)

*All models use the same stratified 80/20 train/test split and handle class imbalance.*

#### Individual Model Notebooks:
1. **06a_Churn_LogisticRegression.ipynb**: Standardized baseline with L2 regularization and feature weight interpretation.
2. **06b_Churn_DecisionTree.ipynb**: Visualizable decision tree with pruning to prevent overfitting.
3. **06c_Churn_RandomForest.ipynb**: 200-estimator ensemble with out-of-bag scoring and Gini importance plots.
4. **06d_Churn_XGBoost_SHAP.ipynb**: Gradient boosted trees with full SHAP explainability (beeswarm summary, waterfall plots, dependence charts).
5. **06e_Churn_LightGBM.ipynb**: Fast histogram-based gradient boosting with leaf-wise tree growth.
6. **06f_Churn_SVM.ipynb**: Support Vector Machine with Radial Basis Function (RBF) kernel and probability calibration.
7. **06g_Churn_MLP_NeuralNet.ipynb**: Multi-Layer Perceptron neural network with early stopping and loss convergence monitoring.

#### Comparison & Selection:
8. **06h_Churn_Comparison_and_Selection.ipynb**:
   - Computes comparative table: AUC-ROC (target $\ge 0.88$), Accuracy, Precision, Recall, F1-Score, and Precision@Top20%.
   - Overlays all 7 ROC curves on a single plot with AUC scores.
   - Compares confusion matrices across top candidates.
   - Runs Optuna hyperparameter optimization on the top 2 models to produce the final champion.
   - **Selects and promotes**: `models/best_churn_model.pkl`.

---

### Phase 5: Business Optimization, Grand Evaluation & Dashboard

- **07_Inventory_Optimization.ipynb**: Consumes the winning demand forecast to calculate Safety Stock ($Z \cdot \sigma \cdot \sqrt{L}$), Reorder Point (ROP), and Economic Order Quantity (EOQ). Classifies products into Critical, Low, Adequate, and Overstock.
- **08_Grand_Model_Evaluation_and_Pipeline.ipynb**: Compiles the master leaderboard of all 18 models across all three domains into an executive-level summary and packages the production pipeline.
- **09_Drift_Detection_and_Monitoring.ipynb**: Sets up Evidently AI data drift and target drift reports for production monitoring.
- **10_Dashboard_Data_Preparation.ipynb**: Pre-computes and caches all metrics, plots, and prediction tables into `dashboard/data/` for sub-second Streamlit rendering.

---

## 4. Complete Project Directory Layout

```
RetailPulse/
│
├── data/
│   ├── raw/                                      # Original raw Excel/CSV files
│   ├── processed/                                # Cleaned & feature-engineered data
│   │   ├── cleaned_transactions.csv
│   │   ├── rfm_features.csv
│   │   ├── timeseries_features.csv
│   │   ├── churn_features.csv
│   │   ├── customer_segments.csv                 # Promoted from 04e
│   │   └── inventory_recommendations.csv         # Produced by 07
│   └── predictions/                              # Predictions from each individual model
│       ├── seg_kmeans.csv
│       ├── seg_dbscan.csv
│       ├── forecast_arima.csv
│       ├── forecast_prophet.csv
│       ├── forecast_lstm.csv
│       ├── churn_xgboost.csv
│       └── ...
│
├── models/                                       # Serialized model binaries
│   ├── seg_kmeans.pkl
│   ├── forecast_prophet.pkl
│   ├── churn_xgboost.pkl
│   ├── best_segmentation.pkl                     # Selected winner
│   ├── best_forecaster.pkl                       # Selected winner
│   └── best_churn_model.pkl                      # Selected winner
│
├── notebooks/
│   ├── 01_data_pipeline/
│   ├── 02_customer_segmentation/
│   ├── 03_demand_forecasting/
│   ├── 04_churn_prediction/
│   └── 05_business_optimization/
│
├── reports/
│   ├── metrics/                                  # JSON/CSV metric leaderboards
│   │   ├── segmentation_metrics.json
│   │   ├── forecasting_metrics.json
│   │   └── churn_metrics.json
│   ├── figures/                                  # Diagnostic and comparison charts
│   └── drift/                                    # Evidently AI HTML drift reports
│
├── dashboard/                                    # Interactive Streamlit application
│   ├── app.py
│   ├── pages/
│   │   ├── 1_📊_Overview.py
│   │   ├── 2_👥_Customer_Segmentation.py
│   │   ├── 3_📈_Demand_Forecasting.py
│   │   ├── 4_⚠️_Churn_Risk_Analysis.py
│   │   ├── 5_📦_Inventory_Optimization.py
│   │   └── 6_🏆_Model_Leaderboard.py
│   └── data/                                     # Fast-loading dashboard tables
│
├── requirements.txt
├── README.md
└── RetailPulse_Project_Guide.md
```

---

## 5. Execution Order

```
[01 Ingestion & Clean] ──▶ [02 EDA] ──▶ [03 Feature Engineering]
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
   [Segmentation Models]              [Forecasting Models]                 [Churn Models]
   04a KMeans                         05a ARIMA                           06a Logistic Regression
   04b DBSCAN                         05b SARIMA                          06b Decision Tree
   04c Agglomerative                  05c Prophet                         06c Random Forest
   04d GMM                            05d LSTM                            06d XGBoost (SHAP)
             │                        05e XGBoost                         06e LightGBM
             ▼                        05f Random Forest                   06f SVM
   [04e Compare & Select Winner]      05g Ensemble                        06g MLP Neural Net
                                               │                                     │
                                               ▼                                     ▼
                                  [05h Compare & Select Winner]       [06h Compare & Select Winner]
                                               │                                     │
                                               ▼                                     │
                                  [07 Inventory Optimization]                        │
                                               │                                     │
                                               └───────────────────┬─────────────────┘
                                                                   ▼
                                                [08 Grand Leaderboard & Pipeline]
                                                                   ▼
                                                [09 Drift Detection & Monitoring]
                                                                   ▼
                                                [10 Dashboard Data Preparation]
                                                                   ▼
                                                    [Streamlit Dashboard]
```
