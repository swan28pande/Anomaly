import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import pandas as pd
import numpy as np
import os
import joblib

class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, input_dim)
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

class AutoencoderModel:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.threshold = None
        self.input_dim = None
        
    def _build_preprocessor(self, df):
        categorical_features = ['category', 'location']
        numerical_features = ['amount']
        
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
        numerical_transformer = StandardScaler()
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        self.preprocessor.fit(df)
        
    def train(self, df: pd.DataFrame, epochs=20, batch_size=32):
        if self.preprocessor is None:
            self._build_preprocessor(df)
            
        X = self.preprocessor.transform(df)
        self.input_dim = X.shape[1]
        
        # Convert to PyTorch tensors
        X_tensor = torch.FloatTensor(X)
        
        self.model = Autoencoder(self.input_dim)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Training loop
        dataset = torch.utils.data.TensorDataset(X_tensor, X_tensor)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.model.train()
        for epoch in range(epochs):
            for data in dataloader:
                inputs, _ = data
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, inputs)
                loss.backward()
                optimizer.step()
                
        # Determine threshold
        self.model.eval()
        with torch.no_grad():
            reconstructions = self.model(X_tensor)
            mse = torch.mean(torch.pow(X_tensor - reconstructions, 2), dim=1).numpy()
            
        self.threshold = np.percentile(mse, 95)
        print(f"Autoencoder trained. Threshold set to: {self.threshold}")
        
    def predict(self, df: pd.DataFrame):
        if self.model is None or self.preprocessor is None:
            raise Exception("Model not trained yet.")
            
        X = self.preprocessor.transform(df)
        X_tensor = torch.FloatTensor(X)
        
        self.model.eval()
        with torch.no_grad():
            reconstructions = self.model(X_tensor)
            mse = torch.mean(torch.pow(X_tensor - reconstructions, 2), dim=1).numpy()
        
        return [1 if error > self.threshold else 0 for error in mse]
        
    def save(self, model_path="backend/models/autoencoder.pth", preproc_path="backend/models/autoencoder_preproc.joblib"):
        if self.model:
            torch.save(self.model.state_dict(), model_path)
            # Save input dim as well to rebuild model
            with open("backend/models/ae_config.txt", "w") as f:
                f.write(str(self.input_dim))
        if self.preprocessor:
            joblib.dump(self.preprocessor, preproc_path)
        if self.threshold:
            with open("backend/models/ae_threshold.txt", "w") as f:
                f.write(str(self.threshold))

    def load(self, model_path="backend/models/autoencoder.pth", preproc_path="backend/models/autoencoder_preproc.joblib"):
        if os.path.exists(preproc_path):
            self.preprocessor = joblib.load(preproc_path)
        
        if os.path.exists("backend/models/ae_config.txt"):
            with open("backend/models/ae_config.txt", "r") as f:
                self.input_dim = int(f.read())
                
        if os.path.exists(model_path) and self.input_dim:
            self.model = Autoencoder(self.input_dim)
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()
            
        if os.path.exists("backend/models/ae_threshold.txt"):
            with open("backend/models/ae_threshold.txt", "r") as f:
                self.threshold = float(f.read())
