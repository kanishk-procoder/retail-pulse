# RetailPulse – AI-Powered Customer Analytics & Demand Forecasting Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Gradient%20Boosting-15B8A6?style=flat)](https://xgboost.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **RetailPulse** is an enterprise-grade retail intelligence platform that ingests real-world transactional data to deliver predictive demand forecasts, behavioral customer segmentation, early-warning churn risk classification, and prescriptive inventory optimization.

---

## 📌 Key Capabilities

- **Customer Segmentation**: RFM behavioral clustering benchmarking **K-Means**, **DBSCAN**, **Agglomerative**, and **Gaussian Mixture Models (GMM)**.
- **Demand Forecasting**: 30-day ahead revenue forecasting evaluating **ARIMA**, **SARIMA**, **Prophet**, **PyTorch LSTM**, **XGBoost Regressor**, **Random Forest**, and **Ensembles**.
- **Customer Churn Prevention**: Supervised classification using **Random Forest**, **LightGBM**, **XGBoost (with SHAP)**, **Decision Trees**, **SVM**, **MLP Neural Networks**, and **Logistic Regression**.
- **Inventory Optimization**: Data-driven calculation of **Safety Stock**, **Reorder Points (ROP)**, and **Economic Order Quantities (EOQ)** preventing stockouts.
- **Interactive Multi-Page Streamlit Dashboard**: What-if scenario analysis, 3D RFM cluster exploration, SHAP explainability, and purchase order generators.

---

## 🏗️ Repository Architecture

```text
RetailPulse/
│
├── data/
│   ├── raw/                             # Original UCI Online Retail II dataset
│   ├── processed/                       # Cleaned, RFM, and time-series data
│   └── predictions/                     # Out-of-sample predictions per model
│
├── models/                              # Serialized champion and candidate models (.pkl, .pt)
│   ├── best_segmentation.pkl            # Champion K-Means model
│   ├── best_forecaster.pkl              # Champion PyTorch LSTM forecaster
│   ├── best_churn_model.pkl             # Champion Random Forest classifier
│   └── segmentation_scaler.pkl
│
├── notebooks/                           # 28 Modular Jupyter Notebooks
│   ├── 01_data_pipeline/                # Data Loading, EDA, Feature Engineering
│   ├── 02_customer_segmentation/        # KMeans, DBSCAN, Agglomerative, GMM, Comparison
│   ├── 03_demand_forecasting/           # ARIMA, SARIMA, Prophet, LSTM, XGBoost, RF, Ensemble, Comparison
│   ├── 04_churn_prediction/             # LR, DT, RF, XGBoost+SHAP, LightGBM, SVM, MLP, Comparison
│   └── 05_business_optimization/        # Inventory, Grand Evaluation, Drift, Dashboard Prep
│
├── reports/
│   ├── metrics/                         # Master JSON/CSV benchmark leaderboards
│   └── figures/                         # Visualizations and diagnostic plots
│
├── dashboard/                           # Multi-page Streamlit Dashboard
│   ├── app.py                           # Executive Overview & KPIs
│   ├── pages/
│   │   ├── 2_👥_Customer_Segmentation.py
│   │   ├── 3_📈_Demand_Forecasting.py
│   │   ├── 4_⚠️_Churn_Risk_Analysis.py
│   │   ├── 5_📦_Inventory_Optimization.py
│   │   └── 6_🏆_Model_Leaderboard.py
│   └── data/                            # Fast-loading pre-computed caches
│
├── src/                                 # Reproducible Python Pipeline Scripts
│   ├── preprocess.py
│   ├── features.py
│   ├── train_segmentation.py
│   ├── train_forecasting.py
│   ├── train_churn.py
│   ├── inventory.py
│   └── prepare_dashboard_data.py
│
├── requirements.txt
├── .gitignore
├── RetailPulse_Project_Guide.md
└── RetailPulse_Implementation_Plan.md
```

---

## ⚡ Quickstart Guide

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository
git clone https://github.com/your-username/RetailPulse.git
cd RetailPulse

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full End-to-End Pipeline

To process raw data, train all 18 models, and prepare dashboard data:

```bash
# 1. Ingestion & Preprocessing
python src/preprocess.py

# 2. Feature Engineering (RFM, Time-Series, Churn)
python src/features.py

# 3. Train & Benchmark Segmentation Models
python src/train_segmentation.py

# 4. Train & Benchmark Forecasting Models
python src/train_forecasting.py

# 5. Train & Benchmark Churn Classifiers
python src/train_churn.py

# 6. Prescriptive Inventory Optimization
python src/inventory.py

# 7. Prepare Dashboard Cached Data
python src/prepare_dashboard_data.py
```

### 3. Launch the Interactive Dashboard

```bash
streamlit run dashboard/app.py
```
Open your browser to `http://localhost:8501`.

---

## 🏆 Model Benchmark Results

### 1. Demand Forecasting (30-Day Holdout)
| Rank | Architecture | MAPE (%) ↓ | RMSE (£) ↓ | R² Score ↑ | Selection |
|:---:|:---|:---:|:---:|:---:|:---:|
| 🥇 | **PyTorch LSTM** | **21.63%** | **£29,326** | **0.2053** | **Champion** |
| 2 | XGBoost Regressor | 23.20% | £29,546 | 0.1934 | Alternate |
| 3 | Hybrid Ensemble | 24.14% | £29,802 | 0.1793 | Alternate |
| 4 | Random Forest | 24.35% | £28,462 | 0.2515 | Alternate |
| 5 | Facebook Prophet | 25.09% | £30,394 | 0.1464 | Alternate |
| 6 | ARIMA(1,1,1) | 33.88% | £33,860 | -0.0594 | Baseline |
| 7 | SARIMA(1,1,1)x(1,0,1,7) | 100.0% | £54,913 | -1.7862 | Baseline |

### 2. Customer Churn Prediction (80/20 Test Holdout)
| Rank | Classifier | AUC-ROC ↑ | Accuracy ↑ | F1-Score ↑ | Precision@Top20% ↑ | Selection |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 🥇 | **Random Forest** | **0.8200** | **0.7440** | **0.7609** | **0.8213** | **Champion** |
| 2 | LightGBM | 0.8193 | 0.7457 | 0.7644 | 0.8255 | Alternate |
| 3 | XGBoost (SHAP) | 0.8172 | 0.7423 | 0.7597 | 0.8340 | Alternate |
| 4 | Decision Tree | 0.8040 | 0.7415 | 0.7576 | 0.8000 | Alternate |
| 5 | MLP Neural Net | 0.8029 | 0.7432 | 0.7677 | 0.7957 | Alternate |
| 6 | SVM (RBF) | 0.7963 | 0.7355 | 0.7557 | 0.7745 | Alternate |
| 7 | Logistic Regression | 0.7927 | 0.7177 | 0.7365 | 0.7957 | Baseline |

### 3. Customer Segmentation (RFM Features)
| Rank | Algorithm | Clusters | Silhouette Score ↑ | Calinski-Harabasz ↑ | Davies-Bouldin ↓ | Selection |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 🥇 | **K-Means** | **5** | **0.3425** | **4,848.23** | **0.9497** | **Champion** |
| 2 | Agglomerative | 5 | 0.2862 | 3,884.19 | 1.0462 | Alternate |
| 3 | DBSCAN | 2 | 0.2785 | 2,899.86 | 1.0040 | Alternate |
| 4 | Gaussian Mixture | 5 | 0.1999 | 2,847.41 | 1.2674 | Alternate |

---

## 📦 Prescriptive Inventory Engine

- **Evaluated Products**: 4,305 active SKUs.
- **Critical Risk Items**: 1,013 products requiring urgent supplier orders (£384k revenue protected).
- **Reorder Triggered**: 376 products below Reorder Point (ROP).
- **Optimal Buffers**: 1,952 products maintained in healthy equilibrium.
- **Overstock Alerts**: 964 products flagged with £228k in excess working capital identified.

---

## 🛡️ License

This project is licensed under the MIT License - see the LICENSE file for details.

