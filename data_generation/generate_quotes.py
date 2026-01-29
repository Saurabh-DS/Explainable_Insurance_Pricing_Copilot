import sqlite3
import pandas as pd
import numpy as np
import os

def generate_quotes(n_samples=1500):
    np.random.seed(42)
    
    # Generate random features
    ages = np.random.randint(18, 80, n_samples)
    postcode_risk = np.random.uniform(0, 1, n_samples)
    vehicle_groups = np.random.randint(1, 51, n_samples)
    claims_counts = np.random.randint(0, 6, n_samples)
    ncb_years = np.random.randint(0, 11, n_samples)
    
    # Create DataFrame
    df = pd.DataFrame({
        'age': ages,
        'postcode_risk': postcode_risk,
        'vehicle_group': vehicle_groups,
        'claims_count': claims_counts,
        'ncb_years': ncb_years
    })
    
    # Hidden pricing formula
    def calculate_premium(row):
        base_rate = 500
        
        # Age effect
        if row['age'] < 21:
            age_factor = 1.5
        elif row['age'] < 26:
            age_factor = 1.2
        elif row['age'] > 65:
            age_factor = 1.15
        else:
            age_factor = 1.0
            
        # Vehicle group effect
        vehicle_factor = 1.0 + (row['vehicle_group'] - 1) * 0.05
        
        # Postcode risk effect
        postcode_factor = 1.0 + (row['postcode_risk'] - 0.5) * 0.4
        
        # Claims effect
        claims_factor = 1.0 + row['claims_count'] * 0.2
        
        # NCB effect
        ncb_factor = max(0.5, 1.0 - row['ncb_years'] * 0.05)
        
        premium = base_rate * age_factor * vehicle_factor * postcode_factor * claims_factor * ncb_factor
        return round(premium, 2)
    
    df['premium'] = df.apply(calculate_premium, axis=1)
    
    # Save to SQLite
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/quotes.db')
    df.to_sql('quotes', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"Generated {n_samples} quotes and saved to database/quotes.db")

if __name__ == "__main__":
    generate_quotes()
