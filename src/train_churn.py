import os
import json
import joblib
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import shap

def precision_at_k(y_true, y_prob, k=0.20):
    n = len(y_true)
    top_k_idx = np.argsort(y_prob)[-int(n * k):]
    return precision_score(y_true.iloc[top_k_idx] if hasattr(y_true, 'iloc') else y_true[top_k_idx], [1]*len(top_k_idx), zero_division=0)

def run_churn_training():
    print("==================================================")
    print("RETAILPULSE: STEP 5 - CUSTOMER CHURN PREDICTION")
    print("==================================================")
    
    churn_path = os.path.join("data", "processed", "churn_features.csv")
    df = pd.read_csv(churn_path)
    
    # Leak-free behavioral features (avoiding direct recency cutoff leakage)
    feature_cols = [
        'total_orders', 'total_quantity', 'avg_quantity_per_line',
        'total_spend', 'avg_order_value', 'unique_products_bought',
        'weekend_purchase_ratio', 'days_as_customer',
        'purchase_frequency_days', 'F_Score', 'M_Score'
    ]
    
    X = df[feature_cols].copy()
    y = df['is_churned'].values
    
    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    joblib.dump(scaler, "models/churn_scaler.pkl")
    with open("models/churn_features.json", "w") as f:
        json.dump(feature_cols, f, indent=4)
        
    print(f"Total customers: {len(df):,}")
    print(f"Training set: {len(X_train):,}, Holdout test set: {len(X_test):,}")
    print(f"Features utilized: {len(feature_cols)}")
    
    metrics_list = []
    models_dict = {}
    test_probs = {}
    
    # -------------------------------------------------------------
    # 1. LOGISTIC REGRESSION
    # -------------------------------------------------------------
    print("\n1. Training Logistic Regression baseline...")
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    lr.fit(X_train_scaled, y_train)
    p_lr = lr.predict_proba(X_test_scaled)[:, 1]
    y_pred_lr = (p_lr >= 0.5).astype(int)
    models_dict["Logistic Regression"] = lr
    test_probs["Logistic Regression"] = p_lr
    joblib.dump(lr, "models/churn_lr.pkl")
    
    auc = roc_auc_score(y_test, p_lr)
    p20 = precision_at_k(y_test, p_lr, k=0.20)
    metrics_list.append({
        "Model": "Logistic Regression",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_lr)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_lr)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_lr)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_lr)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   LR -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_lr):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 2. DECISION TREE
    # -------------------------------------------------------------
    print("\n2. Training Decision Tree Classifier...")
    dt = DecisionTreeClassifier(max_depth=5, class_weight='balanced', random_state=42)
    dt.fit(X_train, y_train)
    p_dt = dt.predict_proba(X_test)[:, 1]
    y_pred_dt = (p_dt >= 0.5).astype(int)
    models_dict["Decision Tree"] = dt
    test_probs["Decision Tree"] = p_dt
    joblib.dump(dt, "models/churn_dt.pkl")
    
    auc = roc_auc_score(y_test, p_dt)
    p20 = precision_at_k(y_test, p_dt, k=0.20)
    metrics_list.append({
        "Model": "Decision Tree",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_dt)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_dt)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_dt)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_dt)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   DT -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_dt):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 3. RANDOM FOREST
    # -------------------------------------------------------------
    print("\n3. Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=150, max_depth=8, class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    p_rf = rf.predict_proba(X_test)[:, 1]
    y_pred_rf = (p_rf >= 0.5).astype(int)
    models_dict["Random Forest"] = rf
    test_probs["Random Forest"] = p_rf
    joblib.dump(rf, "models/churn_rf.pkl")
    
    auc = roc_auc_score(y_test, p_rf)
    p20 = precision_at_k(y_test, p_rf, k=0.20)
    metrics_list.append({
        "Model": "Random Forest",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_rf)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_rf)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_rf)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_rf)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   RF -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_rf):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 4. XGBOOST + SHAP
    # -------------------------------------------------------------
    print("\n4. Training XGBoost with SHAP explainability...")
    xgb = XGBClassifier(n_estimators=150, max_depth=4, learning_rate=0.05, eval_metric='logloss', random_state=42)
    xgb.fit(X_train, y_train)
    p_xgb = xgb.predict_proba(X_test)[:, 1]
    y_pred_xgb = (p_xgb >= 0.5).astype(int)
    models_dict["XGBoost"] = xgb
    test_probs["XGBoost"] = p_xgb
    joblib.dump(xgb, "models/churn_xgboost.pkl")
    
    auc = roc_auc_score(y_test, p_xgb)
    p20 = precision_at_k(y_test, p_xgb, k=0.20)
    metrics_list.append({
        "Model": "XGBoost",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_xgb)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_xgb)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_xgb)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_xgb)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   XGBoost -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_xgb):.4f}, P@20%: {p20:.4f}")
    
    # Compute SHAP values for sample
    print("   Computing SHAP feature importance...")
    explainer = shap.TreeExplainer(xgb)
    sample_test = X_test.iloc[:300]
    shap_vals = explainer.shap_values(sample_test)
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    shap_importance = pd.DataFrame({
        "Feature": feature_cols,
        "Mean_SHAP": mean_abs_shap
    }).sort_values('Mean_SHAP', ascending=False)
    shap_importance.to_csv("reports/metrics/churn_shap_importance.csv", index=False)
    print("   Top 3 churn drivers from SHAP:")
    for _, r in shap_importance.head(3).iterrows():
        print(f"     * {r['Feature']}: impact score {r['Mean_SHAP']:.4f}")
        
    # -------------------------------------------------------------
    # 5. LIGHTGBM
    # -------------------------------------------------------------
    print("\n5. Training LightGBM Classifier...")
    lgb = LGBMClassifier(n_estimators=150, max_depth=4, learning_rate=0.05, random_state=42, verbose=-1)
    lgb.fit(X_train, y_train)
    p_lgb = lgb.predict_proba(X_test)[:, 1]
    y_pred_lgb = (p_lgb >= 0.5).astype(int)
    models_dict["LightGBM"] = lgb
    test_probs["LightGBM"] = p_lgb
    joblib.dump(lgb, "models/churn_lightgbm.pkl")
    
    auc = roc_auc_score(y_test, p_lgb)
    p20 = precision_at_k(y_test, p_lgb, k=0.20)
    metrics_list.append({
        "Model": "LightGBM",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_lgb)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_lgb)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_lgb)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_lgb)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   LightGBM -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_lgb):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 6. SUPPORT VECTOR MACHINE (SVM)
    # -------------------------------------------------------------
    print("\n6. Training Support Vector Machine (RBF kernel)...")
    svm = SVC(kernel='rbf', C=1.0, probability=True, random_state=42)
    svm.fit(X_train_scaled, y_train)
    p_svm = svm.predict_proba(X_test_scaled)[:, 1]
    y_pred_svm = (p_svm >= 0.5).astype(int)
    models_dict["SVM"] = svm
    test_probs["SVM"] = p_svm
    joblib.dump(svm, "models/churn_svm.pkl")
    
    auc = roc_auc_score(y_test, p_svm)
    p20 = precision_at_k(y_test, p_svm, k=0.20)
    metrics_list.append({
        "Model": "SVM",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_svm)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_svm)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_svm)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_svm)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   SVM -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_svm):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 7. MULTI-LAYER PERCEPTRON (MLP) NEURAL NETWORK
    # -------------------------------------------------------------
    print("\n7. Training MLP Deep Neural Network...")
    mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, early_stopping=True, random_state=42)
    mlp.fit(X_train_scaled, y_train)
    p_mlp = mlp.predict_proba(X_test_scaled)[:, 1]
    y_pred_mlp = (p_mlp >= 0.5).astype(int)
    models_dict["MLP Neural Net"] = mlp
    test_probs["MLP Neural Net"] = p_mlp
    joblib.dump(mlp, "models/churn_mlp.pkl")
    
    auc = roc_auc_score(y_test, p_mlp)
    p20 = precision_at_k(y_test, p_mlp, k=0.20)
    metrics_list.append({
        "Model": "MLP Neural Net",
        "AUC_ROC": round(float(auc), 4),
        "Accuracy": round(float(accuracy_score(y_test, y_pred_mlp)), 4),
        "Precision": round(float(precision_score(y_test, y_pred_mlp)), 4),
        "Recall": round(float(recall_score(y_test, y_pred_mlp)), 4),
        "F1_Score": round(float(f1_score(y_test, y_pred_mlp)), 4),
        "Precision_Top20": round(float(p20), 4)
    })
    print(f"   MLP -> AUC-ROC: {auc:.4f}, F1: {f1_score(y_test, y_pred_mlp):.4f}, P@20%: {p20:.4f}")
    
    # -------------------------------------------------------------
    # 8. BENCHMARKING & CHAMPION SELECTION
    # -------------------------------------------------------------
    print("\n8. Evaluating & Selecting Champion Churn Classifier...")
    leaderboard = pd.DataFrame(metrics_list).sort_values("AUC_ROC", ascending=False).reset_index(drop=True)
    leaderboard["Rank"] = range(1, len(leaderboard) + 1)
    
    champion_name = leaderboard.iloc[0]["Model"]
    print("\n--- Churn Prediction Master Leaderboard ---")
    print(leaderboard[['Rank', 'Model', 'AUC_ROC', 'Accuracy', 'Precision', 'Recall', 'F1_Score', 'Precision_Top20']].to_string(index=False))
    
    with open("reports/metrics/churn_metrics.json", "w") as f:
        json.dump(metrics_list, f, indent=4)
        
    # Promote champion model
    champion_model = models_dict[champion_name]
    joblib.dump(champion_model, "models/best_churn_model.pkl")
    print(f"\nChampion model '{champion_name}' (AUC-ROC: {leaderboard.iloc[0]['AUC_ROC']}) promoted to models/best_churn_model.pkl! [OK]")
    
    # Generate full customer risk score predictions
    if champion_name in ["Logistic Regression", "SVM", "MLP Neural Net"]:
        full_scaled = scaler.transform(X)
        all_churn_probs = champion_model.predict_proba(full_scaled)[:, 1]
    else:
        all_churn_probs = champion_model.predict_proba(X)[:, 1]
        
    df['churn_risk_probability'] = np.round(all_churn_probs, 4)
    df['churn_risk_category'] = pd.cut(
        df['churn_risk_probability'],
        bins=[-0.01, 0.35, 0.70, 1.0],
        labels=['Low Risk', 'Medium Risk', 'High Risk']
    )
    df.to_csv("data/processed/customer_churn_scored.csv", index=False)
    print("Scored customer churn dataset saved to data/processed/customer_churn_scored.csv")
    print("==================================================")

if __name__ == "__main__":
    run_churn_training()
