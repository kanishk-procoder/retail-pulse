import os
import glob
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def run_all_notebooks():
    print("==================================================")
    print("EXECUTING ALL NOTEBOOKS TO EMBED OUTPUTS & CHARTS")
    print("==================================================")
    
    # Ordered list of notebooks to execute
    notebook_files = [
        "notebooks/01_data_pipeline/01_Data_Loading_and_Preprocessing.ipynb",
        "notebooks/01_data_pipeline/02_Exploratory_Data_Analysis.ipynb",
        "notebooks/01_data_pipeline/03_Feature_Engineering.ipynb",
        
        "notebooks/02_customer_segmentation/04a_Segmentation_KMeans.ipynb",
        "notebooks/02_customer_segmentation/04b_Segmentation_DBSCAN.ipynb",
        "notebooks/02_customer_segmentation/04c_Segmentation_Agglomerative.ipynb",
        "notebooks/02_customer_segmentation/04d_Segmentation_GMM.ipynb",
        "notebooks/02_customer_segmentation/04e_Segmentation_Comparison_and_Selection.ipynb",
        
        "notebooks/03_demand_forecasting/05a_Forecasting_ARIMA.ipynb",
        "notebooks/03_demand_forecasting/05b_Forecasting_SARIMA.ipynb",
        "notebooks/03_demand_forecasting/05c_Forecasting_Prophet.ipynb",
        "notebooks/03_demand_forecasting/05d_Forecasting_LSTM.ipynb",
        "notebooks/03_demand_forecasting/05e_Forecasting_XGBoost.ipynb",
        "notebooks/03_demand_forecasting/05f_Forecasting_RandomForest.ipynb",
        "notebooks/03_demand_forecasting/05g_Forecasting_Ensemble.ipynb",
        "notebooks/03_demand_forecasting/05h_Forecasting_Comparison_and_Selection.ipynb",
        
        "notebooks/04_churn_prediction/06a_Churn_LogisticRegression.ipynb",
        "notebooks/04_churn_prediction/06b_Churn_DecisionTree.ipynb",
        "notebooks/04_churn_prediction/06c_Churn_RandomForest.ipynb",
        "notebooks/04_churn_prediction/06d_Churn_XGBoost_SHAP.ipynb",
        "notebooks/04_churn_prediction/06e_Churn_LightGBM.ipynb",
        "notebooks/04_churn_prediction/06f_Churn_SVM.ipynb",
        "notebooks/04_churn_prediction/06g_Churn_MLP_NeuralNet.ipynb",
        "notebooks/04_churn_prediction/06h_Churn_Comparison_and_Selection.ipynb",
        
        "notebooks/05_business_optimization/07_Inventory_Optimization.ipynb",
        "notebooks/05_business_optimization/08_Grand_Model_Evaluation_and_Pipeline.ipynb",
        "notebooks/05_business_optimization/09_Drift_Detection_and_Monitoring.ipynb",
        "notebooks/05_business_optimization/10_Dashboard_Data_Preparation.ipynb"
    ]
    
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    
    for idx, nb_path in enumerate(notebook_files, 1):
        if not os.path.exists(nb_path):
            print(f"[{idx}/{len(notebook_files)}] File not found: {nb_path}")
            continue
            
        print(f"[{idx}/{len(notebook_files)}] Executing: {nb_path}...", end="", flush=True)
        try:
            nb_dir = os.path.dirname(nb_path)
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
                
            # Execute in its own directory so relative paths work
            ep.preprocess(nb, {'metadata': {'path': nb_dir}})
            
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            print(" [DONE]")
        except Exception as e:
            print(f" [FAILED: {e}]")
            
    print("\nALL NOTEBOOKS EXECUTED & EMBEDDED WITH OUTPUTS SUCCESSFULLY [OK]")

if __name__ == "__main__":
    run_all_notebooks()

