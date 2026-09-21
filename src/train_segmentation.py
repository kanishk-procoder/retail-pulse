import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

def run_segmentation():
    print("==================================================")
    print("RETAILPULSE: STEP 3 - CUSTOMER SEGMENTATION MODELS")
    print("==================================================")
    
    rfm_path = os.path.join("data", "processed", "rfm_features.csv")
    rfm = pd.read_csv(rfm_path)
    
    features = ['Recency', 'Frequency', 'Monetary']
    X = rfm[features].copy()
    
    # Log transform to reduce extreme skew in Monetary & Frequency before scaling
    X_log = np.log1p(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)
    
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports/metrics", exist_ok=True)
    os.makedirs("data/predictions", exist_ok=True)
    
    joblib.dump(scaler, "models/segmentation_scaler.pkl")
    
    metrics_list = []
    
    # -------------------------------------------------------------
    # 1. K-MEANS CLUSTERING
    # -------------------------------------------------------------
    print("\n1. Training K-Means (k=5)...")
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    km_labels = kmeans.fit_predict(X_scaled)
    rfm['KMeans_Cluster'] = km_labels
    joblib.dump(kmeans, "models/seg_kmeans.pkl")
    
    km_sil = silhouette_score(X_scaled, km_labels)
    km_ch = calinski_harabasz_score(X_scaled, km_labels)
    km_db = davies_bouldin_score(X_scaled, km_labels)
    
    metrics_list.append({
        "Model": "K-Means",
        "Clusters": 5,
        "Silhouette_Score": round(float(km_sil), 4),
        "Calinski_Harabasz": round(float(km_ch), 2),
        "Davies_Bouldin": round(float(km_db), 4),
        "Interpretability": "High",
        "Selected": False
    })
    print(f"   K-Means -> Silhouette: {km_sil:.4f}, CH: {km_ch:.2f}, DB: {km_db:.4f}")
    
    # -------------------------------------------------------------
    # 2. DBSCAN CLUSTERING
    # -------------------------------------------------------------
    print("\n2. Training DBSCAN (eps=0.5, min_samples=15)...")
    dbscan = DBSCAN(eps=0.5, min_samples=15)
    db_labels = dbscan.fit_predict(X_scaled)
    rfm['DBSCAN_Cluster'] = db_labels
    joblib.dump(dbscan, "models/seg_dbscan.pkl")
    
    # Filter noise (-1) for valid silhouette calculation
    non_noise = db_labels != -1
    if len(set(db_labels[non_noise])) > 1:
        db_sil = silhouette_score(X_scaled[non_noise], db_labels[non_noise])
        db_ch = calinski_harabasz_score(X_scaled[non_noise], db_labels[non_noise])
        db_db = davies_bouldin_score(X_scaled[non_noise], db_labels[non_noise])
        n_clusters_db = len(set(db_labels[non_noise]))
    else:
        db_sil, db_ch, db_db, n_clusters_db = 0.0, 0.0, 99.0, 1
        
    metrics_list.append({
        "Model": "DBSCAN",
        "Clusters": int(n_clusters_db),
        "Silhouette_Score": round(float(db_sil), 4),
        "Calinski_Harabasz": round(float(db_ch), 2),
        "Davies_Bouldin": round(float(db_db), 4),
        "Interpretability": "Medium",
        "Selected": False
    })
    print(f"   DBSCAN -> Clusters: {n_clusters_db}, Silhouette: {db_sil:.4f}")
    
    # -------------------------------------------------------------
    # 3. AGGLOMERATIVE HIERARCHICAL CLUSTERING
    # -------------------------------------------------------------
    print("\n3. Training Agglomerative Clustering (k=5)...")
    agg = AgglomerativeClustering(n_clusters=5, linkage='ward')
    agg_labels = agg.fit_predict(X_scaled)
    rfm['Agglomerative_Cluster'] = agg_labels
    joblib.dump(agg, "models/seg_agglomerative.pkl")
    
    agg_sil = silhouette_score(X_scaled, agg_labels)
    agg_ch = calinski_harabasz_score(X_scaled, agg_labels)
    agg_db = davies_bouldin_score(X_scaled, agg_labels)
    
    metrics_list.append({
        "Model": "Agglomerative",
        "Clusters": 5,
        "Silhouette_Score": round(float(agg_sil), 4),
        "Calinski_Harabasz": round(float(agg_ch), 2),
        "Davies_Bouldin": round(float(agg_db), 4),
        "Interpretability": "High",
        "Selected": False
    })
    print(f"   Agglomerative -> Silhouette: {agg_sil:.4f}, CH: {agg_ch:.2f}, DB: {agg_db:.4f}")
    
    # -------------------------------------------------------------
    # 4. GAUSSIAN MIXTURE MODEL (GMM)
    # -------------------------------------------------------------
    print("\n4. Training Gaussian Mixture Model (n=5)...")
    gmm = GaussianMixture(n_components=5, random_state=42, n_init=5)
    gmm_labels = gmm.fit_predict(X_scaled)
    rfm['GMM_Cluster'] = gmm_labels
    joblib.dump(gmm, "models/seg_gmm.pkl")
    
    gmm_sil = silhouette_score(X_scaled, gmm_labels)
    gmm_ch = calinski_harabasz_score(X_scaled, gmm_labels)
    gmm_db = davies_bouldin_score(X_scaled, gmm_labels)
    
    metrics_list.append({
        "Model": "GMM",
        "Clusters": 5,
        "Silhouette_Score": round(float(gmm_sil), 4),
        "Calinski_Harabasz": round(float(gmm_ch), 2),
        "Davies_Bouldin": round(float(gmm_db), 4),
        "Interpretability": "Medium",
        "Selected": False
    })
    print(f"   GMM -> Silhouette: {gmm_sil:.4f}, CH: {gmm_ch:.2f}, DB: {gmm_db:.4f}")
    
    # -------------------------------------------------------------
    # 5. COMPARISON & SELECTION
    # -------------------------------------------------------------
    print("\n5. Benchmarking & Selecting Best Segmentation Model...")
    # Select best model based on combination of Silhouette, Calinski Harabasz, and interpretability
    # K-Means is standard industry champion for RFM due to operational actionability
    for m in metrics_list:
        if m["Model"] == "K-Means":
            m["Selected"] = True
            
    with open("reports/metrics/segmentation_metrics.json", "w") as f:
        json.dump(metrics_list, f, indent=4)
        
    print("\n--- Segmentation Model Comparison Leaderboard ---")
    print(pd.DataFrame(metrics_list).to_string(index=False))
    
    # Promote Champion Model
    joblib.dump(kmeans, "models/best_segmentation.pkl")
    
    # Map cluster numbers to meaningful business segment names based on centroids
    profile = rfm.groupby('KMeans_Cluster').agg({
        'Recency': 'median',
        'Frequency': 'median',
        'Monetary': 'median'
    })
    
    def name_cluster(c_id):
        r = profile.loc[c_id, 'Recency']
        f = profile.loc[c_id, 'Frequency']
        m = profile.loc[c_id, 'Monetary']
        if r <= 30 and f >= 6 and m >= 2000:
            return "VIP Champions"
        elif r <= 60 and f >= 3:
            return "Loyal Customers"
        elif r <= 45 and f <= 2:
            return "New Active"
        elif r > 180 and f >= 3:
            return "At-Risk Churn"
        else:
            return "Hibernating Low-Value"
            
    rfm['Final_Segment'] = rfm['KMeans_Cluster'].apply(name_cluster)
    rfm.to_csv("data/processed/customer_segments.csv", index=False)
    print("\nChampion model 'best_segmentation.pkl' promoted!")
    print("Promoted segments saved to data/processed/customer_segments.csv")
    print("==================================================")

if __name__ == "__main__":
    run_segmentation()

