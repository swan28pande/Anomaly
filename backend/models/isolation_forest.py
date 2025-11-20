from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib
import os

class IsolationForestModel:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = None
        self.preprocessor = None
        
    def _build_pipeline(self):
        categorical_features = ['category', 'location']
        numerical_features = ['amount']
        
        categorical_transformer = OneHotEncoder(handle_unknown='ignore')
        numerical_transformer = StandardScaler()
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])
            
        self.model = Pipeline(steps=[('preprocessor', self.preprocessor),
                                     ('classifier', IsolationForest(contamination=self.contamination, random_state=42))])
                                     
    def train(self, df: pd.DataFrame):
        if self.model is None:
            self._build_pipeline()
            
        # Fit the model
        self.model.fit(df)
        print("Isolation Forest trained.")
        
    def predict(self, df: pd.DataFrame):
        if self.model is None:
            raise Exception("Model not trained yet.")
            
        # Predict returns -1 for outliers and 1 for inliers
        preds = self.model.predict(df)
        # Convert to 1 for anomaly, 0 for normal
        return [1 if x == -1 else 0 for x in preds]
        
    def save(self, path="backend/models/iso_forest.joblib"):
        if self.model:
            joblib.dump(self.model, path)
            
    def load(self, path="backend/models/iso_forest.joblib"):
        if os.path.exists(path):
            self.model = joblib.load(path)
        else:
            print("Model file not found.")
