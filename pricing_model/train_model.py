import sqlite3
import pandas as pd
import lightgbm as lgb
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def train_model():
    # Load data
    if not os.path.exists('database/quotes.db'):
        print("Database not found. Please run data_generation/generate_quotes.py first.")
        return

    conn = sqlite3.connect('database/quotes.db')
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    
    # Prepare features and target
    X = df.drop('premium', axis=1)
    y = df['premium']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train LightGBM Regressor
    model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbose=-1
    )
    model.fit(X_train, y_train)
    
    # Validation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print("--- Training Metrics ---")
    print(f"MAE:  £{mae:.2f}")
    print(f"RMSE: £{rmse:.2f}")
    print(f"R2:   {r2:.4f}")
    print("------------------------")
    
    # Save model and feature list
    os.makedirs('pricing_model', exist_ok=True)
    
    model_data = {
        'model': model,
        'features': X.columns.tolist(),
        'metrics': {
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }
    }
    
    with open('pricing_model/model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Model trained and saved to pricing_model/model.pkl")
    print(f"Features used: {X.columns.tolist()}")

if __name__ == "__main__":
    train_model()
