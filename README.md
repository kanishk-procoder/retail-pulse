# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](<https://img.shields.io/badge/FastAPI-REST%20Engine-009688?style=flat&logo=fastapi&logoColor=white>)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PyTorch](<https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=flat&logo=pytorch&logoColor=white>)](https://pytorch.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![XGBoost](<https://img.shields.io/badge/XGBoost-Gradient%20Boosting-15B8A6?style=flat>)](https://xgboost.readthedocs.io)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **RetailPulse** is an enterprise-grade retail intelligence platform that transforms raw transaction data into proactive business actions: deep learning demand forecasting, behavioral customer segmentation, machine learning churn prevention, and prescriptive warehouse inventory replenishment.

---

## 📌 Key Capabilities

- **Demand Forecasting**: 30-day ahead forward revenue projections evaluating **7 architectures** (**PyTorch LSTM Champion**, XGBoost, Prophet with UK holidays, Random Forest, Hybrid Ensemble, ARIMA, SARIMA).
- **Customer Segmentation**: Behavioral RFM clustering benchmarking **K-Means Champion (5 segments)**, DBSCAN, Agglomerative Hierarchical, and Gaussian Mixture Models (GMM) with single-customer lookup and tailored retention playbooks.
- **Customer Churn Prevention**: Supervised risk classification evaluating **7 models** (**Random Forest Champion** with 82.0% AUC-ROC & 82.1% Precision@Top20%, LightGBM, XGBoost with TreeSHAP, Decision Trees, SVM, MLP Neural Net, Logistic Regression).
- **Prescriptive Inventory Command**: Statistical calculation of **Safety Stock ($SS$)**, **Reorder Points ($ROP$)**, and **Economic Order Quantity ($EOQ$)** across 4,305 active SKUs, safeguarding £384k revenue at risk.
- **Dual Dashboard Architecture**:
  1. **Enterprise Full-Stack SaaS Web App**: High-performance **React 18 + Vite + Tailwind CSS + Recharts** frontend powered by an asynchronous **Python FastAPI REST API**.
  2. **Data Science Exploration Dashboard**: Classic multi-page **Streamlit** dashboard.
- **28 Fully Executed Jupyter Notebooks**: Complete model isolation with embedded outputs, confusion matrix heatmaps, classification reports, and diagnostic plots.

---

## 🏗️ Repository Architecture

```text
RetailPulse/
│
├── backend/                             # Python FastAPI REST API Service
│   └── main.py                          # 17 REST routes with in-memory caching & CORS
│
├── frontend/                            # Modern React 18 + Vite Web Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx              # Collapsible navigation with live status pills
│   │   │   └── Header.jsx               # App header with sync trigger & module metadata
│   │   ├── pages/
│   │   │   ├── Overview.jsx             # Executive KPI cards & revenue velocity charts
│   │   │   ├── Segmentation.jsx         # 5 Segment cards, 2D RFM scatter & customer lookup
│   │   │   ├── Forecasting.jsx          # Multi-model 30D forecast & What-If simulator
│   │   │   ├── ChurnRadar.jsx           # Risk tier donut, TreeSHAP bar & customer queue
│   │   │   ├── InventoryCenter.jsx      # Service level tuner & 4,305 SKU catalog data grid
│   │   │   └── Leaderboard.jsx          # Cross-task 18-model tournament benchmarks
│   │   ├── App.jsx                      # Main app shell and routing
│   │   ├── index.css                    # Tailwind base styles & glassmorphism utilities
│   │   └── main.jsx                     # Vite entry point
│   ├── index.html                       # HTML template with Google Fonts
│   ├── vite.config.js                   # Vite dev server with /api proxy to FastAPI
│   ├── tailwind.config.js               # Custom SaaS color palette
│   ├── postcss.config.js
│   └── package.json                     # Frontend dependencies (Recharts, Lucide, Tailwind)
│
├── dashboard/                           # Classic Multi-Page Streamlit Dashboard
│   ├── app.py                           # Executive Overview
│   ├── pages/
│   │   ├── 2_👥_Customer_Segmentation.py
│   │   ├── 3_📈_Demand_Forecasting.py
│   │   ├── 4_⚠️_Churn_Risk_Analysis.py
│   │   ├── 5_📦_Inventory_Optimization.py
│   │   └── 6_🏆_Model_Leaderboard.py
│   └── data/                            # Fast-loading pre-computed caches
│
├── data/
│   ├── raw/                             # Original UCI Online Retail II dataset (.xlsx)
│   ├── processed/                       # Cleaned Parquet/CSV, RFM, and Churn features
│   └── predictions/                     # Out-of-sample forecast comparison tables
│
├── models/                              # Serialized champion and candidate models (.pkl, .pt)
│   ├── best_segmentation.pkl            # Champion K-Means model
│   ├── best_forecaster.pkl              # Champion PyTorch LSTM forecaster
│   ├── best_churn_model.pkl             # Champion Random Forest classifier
│   └── segmentation_scaler.pkl
│
├── notebooks/                           # 28 Executed Notebooks with Embedded Outputs
│   ├── 01_data_pipeline/                # Data Loading (01), EDA (02), Feature Engineering (03)
│   ├── 02_customer_segmentation/        # KMeans (04a), DBSCAN (04b), Agglomerative (04c), GMM (04d), Comparison (04e)
│   ├── 03_demand_forecasting/           # ARIMA (05a), SARIMA (05b), Prophet (05c), LSTM (05d), XGBoost (05e), RF (05f), Ensemble (05g), Comparison (05h)
│   ├── 04_churn_prediction/             # LR (06a), DT (06b), RF (06c), XGBoost+SHAP (06d), LightGBM (06e), SVM (06f), MLP (06g), Comparison (06h)
│   └── 05_business_optimization/        # Inventory (07), Grand Pipeline (08), Drift (09), Dashboard Prep (10)
│
├── reports/
│   ├── metrics/                         # Master JSON/CSV benchmark leaderboards
│   └── figures/                         # High-resolution diagnostic charts
│
├── src/                                 # Reproducible Python Pipeline Scripts
│   ├── preprocess.py                    # Ingestion, cleaning, outlier winsorization
│   ├── features.py                      # RFM scoring, lag features, leak-free churn targets
│   ├── train_segmentation.py            # Train & evaluate 4 clustering models
│   ├── train_forecasting.py             # Train & evaluate 7 time-series models
│   ├── train_churn.py                   # Train & evaluate 7 churn classifiers with SHAP
│   ├── inventory.py                     # Safety stock, ROP, EOQ policy calculations
│   ├── prepare_dashboard_data.py        # Aggregate cached payloads for dashboards
│   ├── build_all_notebooks.py           # Automated notebook generator with stats & confusion matrices
│   └── execute_all_notebooks.py         # Batch nbconvert executor to embed outputs
│
├── requirements.txt                     # Python dependencies
├── .gitignore
├── RetailPulse_Project_Guide.md
└── RetailPulse_Implementation_Plan.md
```

---

## ⚡ Quickstart Guide

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/kanishk-procoder/retail-pulse.git
cd RetailPulse

# Create & activate Python virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
pip install fastapi uvicorn

# Install Frontend packages
cd frontend
npm install
cd ..
```

---

### 2. Launching the Applications

#### Option A: Modern Enterprise Full-Stack Web App (FastAPI + React)

Run the backend and frontend services:

- **1. Start FastAPI Backend:**

  ```bash
  python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
  ```

  *Interactive Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*
- **2. Start React Frontend:**

  ```bash
  cd frontend
  npm run dev
  ```

  *Live Web Application: [http://localhost:5173](http://localhost:5173)*

#### Option B: Classic Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

*Live Streamlit App: [http://localhost:8501](http://localhost:8501)*

---

### 3. Reproducible Pipeline Execution

To re-run the entire data pipeline from raw data to model training:

```bash
# 1. Data Ingestion & Preprocessing
python src/preprocess.py

# 2. Feature Engineering (RFM, Time-Series, Churn)
python src/features.py

# 3. Model Training & Benchmarking
python src/train_segmentation.py
python src/train_forecasting.py
python src/train_churn.py

# 4. Inventory Optimization & Dashboard Data Packaging
python src/inventory.py
python src/prepare_dashboard_data.py

# 5. Rebuild & Execute All 28 Notebooks with Embedded Outputs
python src/build_all_notebooks.py
python src/execute_all_notebooks.py
```

---

## 🏆 Model Benchmark Results (18 Models Evaluated)

### 1. Demand Forecasting (30-Day Forward Holdout)

| Rank | Architecture                         |   MAPE (%) ↓   |    RMSE (£) ↓    |    MAE (£) ↓    |   R² Score ↑   |          Selection          |
| :--: | :----------------------------------- | :--------------: | :----------------: | :----------------: | :--------------: | :-------------------------: |
|  🥇  | **PyTorch Deep Learning LSTM** | **21.63%** | **£29,326** | **£12,428** | **0.2053** | **Champion Selected** |
|  2  | XGBoost Regressor                    |      23.20%      |      £29,546      |      £12,766      |      0.1934      |     High-Performing ML     |
|  3  | Hybrid Ensemble (Prophet + XGBoost)  |      24.14%      |      £29,802      |      £13,801      |      0.1793      |          Alternate          |
|  4  | Random Forest Regressor              |      24.35%      |      £28,462      |      £12,735      |      0.2515      |          Alternate          |
|  5  | Facebook Prophet                     |      25.09%      |      £30,394      |      £14,718      |      0.1464      |          Alternate          |
|  6  | ARIMA(1, 1, 1)                       |      33.88%      |      £33,860      |      £21,520      |     -0.0594     |          Baseline          |
|  7  | SARIMA(1, 1, 1)x(1, 0, 1, 7)         |      100.0%      |      £54,913      |      £43,968      |     -1.7862     |          Baseline          |

### 2. Customer Churn Prediction (80/20 Stratified Holdout)

| Rank | Classifier                         |    AUC-ROC ↑    |   Accuracy ↑   |   Precision ↑   |    Recall ↑    |   F1-Score ↑   | Precision@Top20% ↑ |          Selection          |
| :--: | :--------------------------------- | :--------------: | :--------------: | :--------------: | :--------------: | :--------------: | :-----------------: | :-------------------------: |
|  🥇  | **Random Forest Classifier** | **0.8200** | **0.7440** | **0.7247** | **0.8010** | **0.7609** |  **0.8213**  | **Champion Selected** |
|  2  | LightGBM                           |      0.8193      |      0.7457      |      0.7228      |      0.8110      |      0.7644      |       0.8255       |      Gradient Boosting      |
|  3  | XGBoost (with TreeSHAP)            |      0.8172      |      0.7423      |      0.7225      |      0.8010      |      0.7597      |       0.8340       |          Top P@20%          |
|  4  | Decision Tree Classifier           |      0.8040      |      0.7415      |      0.7241      |      0.7943      |      0.7576      |       0.8000       |         Rule-Based         |
|  5  | MLP Neural Network                 |      0.8029      |      0.7432      |      0.7108      |      0.8344      |      0.7677      |       0.7957       |        Deep Learning        |
|  6  | Support Vector Machine (RBF)       |      0.7963      |      0.7355      |      0.7126      |      0.8043      |      0.7557      |       0.7745       |        Margin-Based        |
|  7  | Logistic Regression                |      0.7927      |      0.7177      |      0.7009      |      0.7759      |      0.7365      |       0.7957       |       Linear Baseline       |

### 3. Customer Segmentation (Log-Transformed RFM Features)

| Rank | Algorithm                    |  Clusters  | Silhouette Score ↑ | Calinski-Harabasz ↑ | Davies-Bouldin ↓ | Interpretability |          Selection          |
| :--: | :--------------------------- | :---------: | :-----------------: | :------------------: | :---------------: | :--------------: | :-------------------------: |
|  🥇  | **K-Means Clustering** | **5** |  **0.3425**  |  **4,848.23**  | **0.9497** |  **High**  | **Champion Selected** |
|  2  | Agglomerative Hierarchical   |      5      |       0.2862       |       3,884.19       |      1.0462      |       High       |          Alternate          |
|  3  | DBSCAN Density Clustering    |      2      |       0.2785       |       2,899.86       |      1.0040      |      Medium      |          Alternate          |
|  4  | Gaussian Mixture Model (GMM) |      5      |       0.1999       |       2,847.41       |      1.2674      |      Medium      |          Alternate          |

---

## 📦 Prescriptive Inventory Optimization

- **Catalog Coverage**: 4,305 active retail SKUs evaluated.
- **Safety Stock ($SS$)**: $Z \times \sigma_d \times \sqrt{L}$ ($Z=1.65$ for 95% service level, $L=7$ days lead time).
- **Reorder Point ($ROP$)**: $(\bar{d} \times L) + SS$.
- **Economic Order Quantity ($EOQ$)**: $\sqrt{\frac{2 \times D \times S}{H}}$ ($S=£15$ order fee, $H=20\%$ holding cost).
- **Warehouse Health Breakdown**:
  - 🔴 **1,013 Critical SKUs**: Stock below safety buffer (£384k revenue at risk).
  - 🟡 **376 Reorder Triggered**: Below ROP; purchase orders generated.
  - 🟢 **1,952 Optimal**: Balanced stock level.
  - 🔵 **964 Overstocked**: £228k in idle working capital identified.

---

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.
