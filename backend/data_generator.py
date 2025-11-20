import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_transaction_data(num_records=1000, anomaly_fraction=0.05):
    """
    Generates synthetic e-commerce transaction data.
    
    Args:
        num_records (int): Number of transactions to generate.
        anomaly_fraction (float): Fraction of records that should be anomalous.
        
    Returns:
        pd.DataFrame: DataFrame containing transaction data.
    """
    
    # Set seeds for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # User IDs
    user_ids = [f'USER_{i:04d}' for i in range(1, 101)]
    
    # Categories
    categories = ['Electronics', 'Clothing', 'Home', 'Groceries', 'Books']
    
    # Locations
    locations = ['US', 'UK', 'CA', 'DE', 'FR', 'JP']
    
    data = []
    
    start_date = datetime.now() - timedelta(days=30)
    
    num_anomalies = int(num_records * anomaly_fraction)
    num_normal = num_records - num_anomalies
    
    # Generate Normal Data
    for _ in range(num_normal):
        date = start_date + timedelta(minutes=random.randint(0, 30*24*60))
        amount = round(np.random.lognormal(mean=3.0, sigma=1.0), 2) # Lognormal distribution for prices
        # Cap normal amounts reasonably
        if amount > 1000: amount = 1000
        if amount < 1: amount = 1
        
        data.append({
            'transaction_id': f'TXN_{random.randint(100000, 999999)}',
            'user_id': random.choice(user_ids),
            'timestamp': date,
            'amount': amount,
            'category': random.choice(categories),
            'location': random.choice(locations),
            'is_anomaly': 0
        })
        
    # Generate Anomalous Data
    for _ in range(num_anomalies):
        anomaly_type = random.choice(['high_amount', 'unusual_location', 'rapid_transactions'])
        
        date = start_date + timedelta(minutes=random.randint(0, 30*24*60))
        user = random.choice(user_ids)
        
        if anomaly_type == 'high_amount':
            amount = round(np.random.uniform(2000, 10000), 2) # Very high amount
            category = 'Electronics' # Usually high value
            location = random.choice(locations)
        elif anomaly_type == 'unusual_location':
            amount = round(np.random.lognormal(mean=3.0, sigma=1.0), 2)
            category = random.choice(categories)
            location = 'Unknown_Loc' # Strange location
        elif anomaly_type == 'rapid_transactions':
            # Simulate rapid fire transactions by creating a burst around this time
            amount = round(np.random.lognormal(mean=3.0, sigma=1.0), 2)
            category = random.choice(categories)
            location = random.choice(locations)
            # We just add one here, but in a real scenario we'd add multiple. 
            # For simplicity in this row-based gen, we mark it.
            
        data.append({
            'transaction_id': f'TXN_{random.randint(100000, 999999)}',
            'user_id': user,
            'timestamp': date,
            'amount': amount,
            'category': category,
            'location': location,
            'is_anomaly': 1
        })
    
    df = pd.DataFrame(data)
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    df = generate_transaction_data()
    print(df.head())
    print(df['is_anomaly'].value_counts())
    df.to_csv("transactions.csv", index=False)
