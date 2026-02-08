import sqlite3
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def run_model_evaluation():
    """Runs model evaluation and returns metrics."""
    # Load model
    model_path = 'pricing_model/model.pkl'
    if not os.path.exists(model_path):
        return {"error": f"Model not found at {model_path}"}
    
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    model = model_data['model']
    features = model_data['features']
    
    # Load data for evaluation
    db_path = 'database/quotes.db'
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}"}
        
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    
    X = df[features]
    y = df['premium']
    
    # Predict
    y_pred = model.predict(X)
    
    # Calculate Metrics
    mae = mean_absolute_error(y, y_pred)
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    
    # Visualizations
    os.makedirs('evaluation/plots', exist_ok=True)
    
    # 1. Feature Importance
    plt.figure(figsize=(10, 6))
    lgb_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values(by='importance', ascending=False)
    
    sns.barplot(x='importance', y='feature', data=lgb_importance, hue='feature', palette='viridis', legend=False)
    plt.title('Feature Importance (LightGBM)')
    plt.tight_layout()
    plt.savefig('evaluation/plots/feature_importance.png')
    plt.close() # Close plot to free memory
    
    # 2. Predicted vs Actual
    plt.figure(figsize=(8, 8))
    plt.scatter(y, y_pred, alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
    plt.xlabel('Actual Premium (£)')
    plt.ylabel('Predicted Premium (£)')
    plt.title('Predicted vs Actual Premium')
    plt.tight_layout()
    plt.savefig('evaluation/plots/predicted_vs_actual.png')
    plt.close() # Close plot to free memory

    return {
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }

if __name__ == "__main__":
    metrics = run_model_evaluation()
    if "error" in metrics:
        print(metrics["error"])
    else:
        print("\n" + "="*40)
        print("          MODEL EVALUATION REPORT")
        print("="*40)
        print(f"Mean Absolute Error:     £{metrics['mae']:.2f}")
        print(f"Root Mean Squared Error:  £{metrics['rmse']:.2f}")
        print(f"R2 Score:                {metrics['r2']:.4f}")
        print("="*40)
        print("Plots saved to evaluation/plots/")
