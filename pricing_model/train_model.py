import sqlite3
import pandas as pd
import lightgbm as lgb
import pickle
import os

def train_model():
    # Load data
    conn = sqlite3.connect('database/quotes.db')
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    
    # Prepare features and target
    X = df.drop('premium', axis=1)
    y = df['premium']
    
    # Train LightGBM Regressor
    model = lgb.LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        verbose=-1
    )
    model.fit(X, y)
    
    # Save model and feature list
    os.makedirs('pricing_model', exist_ok=True)
    
    model_data = {
        'model': model,
        'features': X.columns.tolist()
    }
    
    with open('pricing_model/model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("Model trained and saved to pricing_model/model.pkl")
    print(f"Features used: {X.columns.tolist()}")

if __name__ == "__main__":
    train_model()
