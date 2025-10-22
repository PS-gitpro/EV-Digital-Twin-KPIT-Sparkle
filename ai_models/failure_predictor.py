import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

print("🤖 AI Failure Predictor for EV Battery")
print("=" * 50)

class BatteryFailurePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        print("✅ AI Predictor initialized")
    
    def generate_training_data(self):
        """Generate synthetic training data for battery failure prediction"""
        print("📊 Generating training data...")
        
        np.random.seed(42)
        n_samples = 1000
        
        # Simulate battery parameters that lead to failure
        data = {
            'voltage_drop_rate': np.random.exponential(0.1, n_samples),
            'temp_increase_rate': np.random.normal(2, 1, n_samples),
            'cycle_count': np.random.randint(100, 2000, n_samples),
            'charge_rate': np.random.uniform(0.5, 2.0, n_samples),
            'internal_resistance': np.random.normal(0.05, 0.02, n_samples)
        }
        
        # Failure probability based on parameters
        failure_risk = (
            data['voltage_drop_rate'] * 0.4 +
            data['temp_increase_rate'] * 0.3 +
            (data['cycle_count'] / 2000) * 0.2 +
            data['internal_resistance'] * 0.1
        )
        
        data['failure_risk'] = np.clip(failure_risk + np.random.normal(0, 0.1, n_samples), 0, 1)
        
        self.df = pd.DataFrame(data)
        print(f"✅ Generated {len(self.df)} training samples")
        return self.df
    
    def train_model(self):
        """Train the AI model"""
        print("🧠 Training AI model...")
        
        X = self.df.drop('failure_risk', axis=1)
        y = self.df['failure_risk']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print("✅ AI model trained successfully!")
        print(f"   - Features: {list(X.columns)}")
        print(f"   - Training score: {self.model.score(X_scaled, y):.3f}")
    
    def predict_failure(self, battery_params):
        """Predict battery failure risk"""
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return None
        
        # Create feature vector
        features = np.array([[
            battery_params.get('voltage_drop_rate', 0.1),
            battery_params.get('temp_increase_rate', 2.0),
            battery_params.get('cycle_count', 500),
            battery_params.get('charge_rate', 1.0),
            battery_params.get('internal_resistance', 0.05)
        ]])
        
        # Scale and predict
        features_scaled = self.scaler.transform(features)
        risk = self.model.predict(features_scaled)[0]
        
        # Interpret results
        if risk < 0.3:
            status = "✅ LOW RISK"
            action = "Continue normal operation"
        elif risk < 0.7:
            status = "⚠️ MEDIUM RISK" 
            action = "Monitor closely, reduce load"
        else:
            status = "🚨 HIGH RISK"
            action = "Immediate maintenance required"
        
        print(f"🔮 Failure Risk Prediction:")
        print(f"   - Risk Score: {risk:.3f}")
        print(f"   - Status: {status}")
        print(f"   - Recommended Action: {action}")
        
        return risk, status, action

if __name__ == "__main__":
    # Demo the AI predictor
    predictor = BatteryFailurePredictor()
    predictor.generate_training_data()
    predictor.train_model()
    
    # Test prediction
    test_battery = {
        'voltage_drop_rate': 0.15,
        'temp_increase_rate': 3.5, 
        'cycle_count': 1200,
        'charge_rate': 1.5,
        'internal_resistance': 0.08
    }
    
    predictor.predict_failure(test_battery)
