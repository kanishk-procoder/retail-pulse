import os
import json
import joblib
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Metrics definitions
def calc_metrics(actual, pred):
    actual = np.array(actual)
    pred = np.array(pred)
    # Avoid zero division
    mask = actual > 0
    mape = np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100
    rmse = np.sqrt(np.mean((actual - pred) ** 2))
    mae = np.mean(np.abs(actual - pred))
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (np.sum((actual - pred) ** 2) / ss_tot) if ss_tot > 0 else 0.0
    return {
        "MAPE": round(float(mape), 2),
        "RMSE": round(float(rmse), 2),
        "MAE": round(float(mae), 2),
        "R2": round(float(r2), 4)
    }

# PyTorch LSTM Definition
class LSTMForecaster(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_dim, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class TimeSeriesSeqDataset(Dataset):
    def __init__(self, data, seq_len=30):
        self.X = []
        self.y = []
        for i in range(len(data) - seq_len):
            self.X.append(data[i:i+seq_len])
            self.y.append(data[i+seq_len])
        self.X = torch.tensor(np.array(self.X), dtype=torch.float32).unsqueeze(-1)
        self.y = torch.tensor(np.array(self.y), dtype=torch.float32).unsqueeze(-1)
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

def run_forecasting():
    print("==================================================")
    print("RETAILPULSE: STEP 4 - DEMAND FORECASTING MODELS")
    print("==================================================")
    
    ts_path = os.path.join("data", "processed", "timeseries_features.csv")
    df = pd.read_csv(ts_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date').reset_index(drop=True)
    
    # 30-day holdout split
    test_days = 30
    train_df = df.iloc[:-test_days].copy()
    test_df = df.iloc[-test_days:].copy()
    
    y_train = train_df['Revenue'].values
    y_test = test_df['Revenue'].values
    test_dates = test_df['Date'].values
    
    print(f"Total time-series history: {len(df)} days")
    print(f"Training set: {len(train_df)} days ({train_df['Date'].min().strftime('%Y-%m-%d')} to {train_df['Date'].max().strftime('%Y-%m-%d')})")
    print(f"Holdout test set: {len(test_df)} days ({test_df['Date'].min().strftime('%Y-%m-%d')} to {test_df['Date'].max().strftime('%Y-%m-%d')})")
    
    predictions_df = pd.DataFrame({
        "Date": test_df['Date'].dt.strftime('%Y-%m-%d'),
        "Actual": y_test
    })
    
    metrics_list = []
    
    # -------------------------------------------------------------
    # 1. ARIMA(1, 1, 1)
    # -------------------------------------------------------------
    print("\n1. Training ARIMA(1, 1, 1)...")
    arima_model = ARIMA(y_train, order=(1, 1, 1)).fit()
    arima_pred = arima_model.forecast(steps=test_days)
    arima_pred = np.clip(arima_pred, 0, None)
    predictions_df['ARIMA'] = np.round(arima_pred, 2)
    joblib.dump(arima_model, "models/forecast_arima.pkl")
    m = calc_metrics(y_test, arima_pred)
    m["Model"] = "ARIMA"
    metrics_list.append(m)
    print(f"   ARIMA -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 2. SARIMA(1, 1, 1)x(1, 0, 1, 7)
    # -------------------------------------------------------------
    print("\n2. Training SARIMA with weekly seasonality (s=7)...")
    sarima_model = SARIMAX(y_train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7)).fit(disp=False)
    sarima_pred = sarima_model.forecast(steps=test_days)
    sarima_pred = np.clip(sarima_pred, 0, None)
    predictions_df['SARIMA'] = np.round(sarima_pred, 2)
    joblib.dump(sarima_model, "models/forecast_sarima.pkl")
    m = calc_metrics(y_test, sarima_pred)
    m["Model"] = "SARIMA"
    metrics_list.append(m)
    print(f"   SARIMA -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 3. PROPHET
    # -------------------------------------------------------------
    print("\n3. Training Facebook Prophet...")
    prophet_df = train_df[['Date', 'Revenue']].rename(columns={'Date': 'ds', 'Revenue': 'y'})
    prophet_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    prophet_model.add_country_holidays(country_name='UK')
    prophet_model.fit(prophet_df)
    
    future = prophet_model.make_future_dataframe(periods=test_days)
    prophet_forecast = prophet_model.predict(future)
    prophet_pred = prophet_forecast.iloc[-test_days:]['yhat'].values
    prophet_pred = np.clip(prophet_pred, 0, None)
    predictions_df['Prophet'] = np.round(prophet_pred, 2)
    joblib.dump(prophet_model, "models/forecast_prophet.pkl")
    m = calc_metrics(y_test, prophet_pred)
    m["Model"] = "Prophet"
    metrics_list.append(m)
    print(f"   Prophet -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 4. PYTORCH LSTM
    # -------------------------------------------------------------
    print("\n4. Training PyTorch Deep Learning LSTM...")
    # Scale series
    mean_val = np.mean(y_train)
    std_val = np.std(y_train) + 1e-6
    y_train_norm = (y_train - mean_val) / std_val
    
    seq_len = 14
    train_ds = TimeSeriesSeqDataset(y_train_norm, seq_len=seq_len)
    loader = DataLoader(train_ds, batch_size=16, shuffle=True)
    
    lstm = LSTMForecaster(input_dim=1, hidden_dim=64, num_layers=2)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(lstm.parameters(), lr=0.005)
    
    lstm.train()
    for epoch in range(40):
        for bx, by in loader:
            optimizer.zero_grad()
            out = lstm(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            
    lstm.eval()
    # Rolling autoregressive forecast for test period
    current_seq = list(y_train_norm[-seq_len:])
    lstm_preds_norm = []
    with torch.no_grad():
        for _ in range(test_days):
            inp = torch.tensor([current_seq[-seq_len:]], dtype=torch.float32).unsqueeze(-1)
            pred_norm = lstm(inp).item()
            lstm_preds_norm.append(pred_norm)
            current_seq.append(pred_norm)
            
    lstm_pred = np.array(lstm_preds_norm) * std_val + mean_val
    lstm_pred = np.clip(lstm_pred, 0, None)
    predictions_df['LSTM'] = np.round(lstm_pred, 2)
    torch.save(lstm.state_dict(), "models/forecast_lstm.pt")
    m = calc_metrics(y_test, lstm_pred)
    m["Model"] = "LSTM (PyTorch)"
    metrics_list.append(m)
    print(f"   LSTM -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 5. XGBOOST REGRESSOR
    # -------------------------------------------------------------
    print("\n5. Training XGBoost Regressor (Lag + Calendar features)...")
    feature_cols = [c for c in df.columns if c not in ['Date', 'Revenue', 'TotalQuantity', 'Transactions', 'UniqueCustomers']]
    
    X_train = train_df[feature_cols]
    X_test = test_df[feature_cols]
    
    xgb = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
    xgb.fit(X_train, y_train)
    xgb_pred = xgb.predict(X_test)
    xgb_pred = np.clip(xgb_pred, 0, None)
    predictions_df['XGBoost'] = np.round(xgb_pred, 2)
    joblib.dump(xgb, "models/forecast_xgboost.pkl")
    m = calc_metrics(y_test, xgb_pred)
    m["Model"] = "XGBoost"
    metrics_list.append(m)
    print(f"   XGBoost -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 6. RANDOM FOREST REGRESSOR
    # -------------------------------------------------------------
    print("\n6. Training Random Forest Regressor...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_pred = np.clip(rf_pred, 0, None)
    predictions_df['RandomForest'] = np.round(rf_pred, 2)
    joblib.dump(rf, "models/forecast_rf.pkl")
    m = calc_metrics(y_test, rf_pred)
    m["Model"] = "Random Forest"
    metrics_list.append(m)
    print(f"   Random Forest -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 7. PROPHET + XGBOOST HYBRID ENSEMBLE
    # -------------------------------------------------------------
    print("\n7. Building Hybrid Ensemble (Prophet + XGBoost blend)...")
    # Weighted blend combining seasonal decomposed Prophet and non-linear XGBoost
    ensemble_pred = 0.55 * prophet_pred + 0.45 * xgb_pred
    predictions_df['Ensemble'] = np.round(ensemble_pred, 2)
    m = calc_metrics(y_test, ensemble_pred)
    m["Model"] = "Hybrid Ensemble"
    metrics_list.append(m)
    print(f"   Hybrid Ensemble -> MAPE: {m['MAPE']}%, RMSE: {m['RMSE']}, R2: {m['R2']}")
    
    # -------------------------------------------------------------
    # 8. BENCHMARKING & SELECTION
    # -------------------------------------------------------------
    print("\n8. Evaluating & Selecting Champion Forecaster...")
    leaderboard = pd.DataFrame(metrics_list).sort_values("MAPE").reset_index(drop=True)
    leaderboard["Rank"] = range(1, len(leaderboard) + 1)
    
    best_model_name = leaderboard.iloc[0]["Model"]
    print("\n--- Demand Forecasting Master Leaderboard ---")
    print(leaderboard[['Rank', 'Model', 'MAPE', 'RMSE', 'MAE', 'R2']].to_string(index=False))
    
    with open("reports/metrics/forecasting_metrics.json", "w") as f:
        json.dump(metrics_list, f, indent=4)
        
    predictions_df.to_csv("data/predictions/forecasting_comparison.csv", index=False)
    print(f"\n30-day predictions saved to data/predictions/forecasting_comparison.csv")
    
    # Promote champion model
    if "Ensemble" in best_model_name:
        champion = {"type": "ensemble", "models": ["prophet", "xgboost"], "weights": [0.55, 0.45]}
        joblib.dump(champion, "models/best_forecaster.pkl")
    elif best_model_name == "Prophet":
        joblib.dump(prophet_model, "models/best_forecaster.pkl")
    elif best_model_name == "XGBoost":
        joblib.dump(xgb, "models/best_forecaster.pkl")
    elif best_model_name == "SARIMA":
        joblib.dump(sarima_model, "models/best_forecaster.pkl")
    else:
        joblib.dump(arima_model, "models/best_forecaster.pkl")
        
    print(f"Champion model '{best_model_name}' promoted to models/best_forecaster.pkl! [OK]")
    print("==================================================")

if __name__ == "__main__":
    run_forecasting()

