from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from backend.data_generator import generate_transaction_data
from backend.models.isolation_forest import IsolationForestModel
from backend.models.autoencoder import AutoencoderModel

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in-memory for simplicity)
DATA_FILE = "transactions.csv"
iso_forest = IsolationForestModel()
autoencoder = AutoencoderModel()

@app.get("/")
def read_root():
    return {"message": "Anomaly Detection API"}

@app.post("/generate-data")
def generate_data(num_records: int = 1000, anomaly_fraction: float = 0.05):
    df = generate_transaction_data(num_records, anomaly_fraction)
    df.to_csv(DATA_FILE, index=False)
    return {"message": f"Generated {num_records} transactions.", "preview": df.head().to_dict(orient="records")}

@app.get("/data")
def get_data(limit: int = 100):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Data not found. Generate data first.")
    df = pd.read_csv(DATA_FILE)
    # Convert timestamp to string for JSON serialization
    df = df.fillna('')
    return df.head(limit).to_dict(orient="records")

@app.post("/train")
def train_models():
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Data not found. Generate data first.")
    
    df = pd.read_csv(DATA_FILE)
    
    # Train Isolation Forest
    iso_forest.train(df)
    iso_forest.save()
    
    # Train Autoencoder
    autoencoder.train(df)
    autoencoder.save()
    
    return {"message": "Models trained successfully."}

@app.get("/detect")
def detect_anomalies(model_type: str = "isolation_forest"):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Data not found. Generate data first.")
    
    df = pd.read_csv(DATA_FILE)
    
    if model_type == "isolation_forest":
        iso_forest.load()
        if not iso_forest.model:
             return {"message": "Model not trained. Please train first."}
        preds = iso_forest.predict(df)
    elif model_type == "autoencoder":
        autoencoder.load()
        if not autoencoder.model:
             return {"message": "Model not trained. Please train first."}
        preds = autoencoder.predict(df)
    else:
        raise HTTPException(status_code=400, detail="Invalid model type.")
    
    df['predicted_anomaly'] = preds
    anomalies = df[df['predicted_anomaly'] == 1]
    
    return {
        "total_records": len(df),
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies.head(100).to_dict(orient="records")
    }

@app.get("/stats")
def get_stats():
    if not os.path.exists(DATA_FILE):
        return {"message": "No data available."}
    
    df = pd.read_csv(DATA_FILE)
    return {
        "total_transactions": len(df),
        "total_amount": float(df['amount'].sum()),
        "avg_amount": float(df['amount'].mean()),
        "categories": df['category'].value_counts().to_dict()
    }
