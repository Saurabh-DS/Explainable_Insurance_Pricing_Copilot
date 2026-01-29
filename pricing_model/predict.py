import pickle
import pandas as pd
import shap
import os
import json
from datetime import datetime

# Load model globally to avoid reloading on every call
MODEL_PATH = 'pricing_model/model.pkl'

def get_model_data():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
    
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)

def predict_premium(profile: dict) -> dict:
    model_data = get_model_data()
    model = model_data['model']
    features = model_data['features']
    
    # Convert profile to DataFrame with correct column order
    df = pd.DataFrame([profile])[features]
    
    # Predict premium
    premium = model.predict(df)[0]
    
    # Calculate SHAP values
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df)
    
    # Format SHAP values for response
    # TreeExplainer might return a list of arrays if it's multi-output, 
    # but for regression it should be a single array.
    if isinstance(shap_values, list):
        shap_vals = shap_values[0][0]
    else:
        shap_vals = shap_values[0]
        
    explanation = {}
    for i, feature in enumerate(features):
        explanation[feature] = float(shap_vals[i])
        
    result = {
        "timestamp": datetime.now().isoformat(),
        "profile": profile,
        "predicted_premium": round(float(premium), 2),
        "shap_values": explanation,
        "base_value": float(explainer.expected_value)
    }
    
    # Log the result
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, 'shap_results.jsonl'), 'a') as f:
        f.write(json.dumps(result) + '\n')
        
    return result

if __name__ == "__main__":
    # Test prediction
    sample_profile = {
        'age': 25,
        'postcode_risk': 0.5,
        'vehicle_group': 15,
        'claims_count': 1,
        'ncb_years': 3
    }
    result = predict_premium(sample_profile)
    print("Prediction Result:")
    print(f"Premium: {result['predicted_premium']}")
    print("SHAP Values (contributions to premium):")
    for feat, val in result['shap_values'].items():
        print(f"  {feat}: {val:+.2f}")
    print(f"Base Value: {result['base_value']:.2f}")
