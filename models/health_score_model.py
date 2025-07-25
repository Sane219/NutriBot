import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class HealthScoreModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        self.scaler = StandardScaler()
        # Updated feature columns for USDA dataset
        self.feature_columns = [
            'Calories', 'Protein', 'TotalFat', 'Carbohydrate', 
            'Sodium', 'SaturatedFat', 'Sugar', 'Calcium', 'Iron', 
            'Potassium', 'VitaminC', 'VitaminE', 'VitaminD'
        ]
        self.is_trained = False
        
    def _calculate_health_score(self, nutrition_data):
        """Calculate health score based on nutrition values using USDA-based scoring"""
        scores = []
        
        for _, row in nutrition_data.iterrows():
            score = 50  # Base score
            
            # Calories (per 100g) - moderate is better
            calories = row.get('Calories', 0)
            if calories <= 100:
                score += 15
            elif calories <= 200:
                score += 10
            elif calories <= 300:
                score += 5
            elif calories > 500:
                score -= 15
            
            # Protein - higher is better
            protein = row.get('Protein', 0)
            if protein >= 20:
                score += 15
            elif protein >= 10:
                score += 10
            elif protein >= 5:
                score += 5
            
            # Total Fat - moderate is better
            fat = row.get('TotalFat', 0)
            if fat <= 3:
                score += 10
            elif fat <= 10:
                score += 5
            elif fat > 30:
                score -= 15
            
            # Saturated Fat - lower is better
            sat_fat = row.get('SaturatedFat', 0)
            if sat_fat <= 1:
                score += 10
            elif sat_fat <= 5:
                score += 5
            elif sat_fat > 10:
                score -= 15
            
            # Sugar - lower is better
            sugar = row.get('Sugar', 0)
            if sugar <= 2:
                score += 10
            elif sugar <= 10:
                score += 5
            elif sugar > 25:
                score -= 15
            
            # Sodium - lower is better
            sodium = row.get('Sodium', 0)
            if sodium <= 100:
                score += 10
            elif sodium <= 300:
                score += 5
            elif sodium > 1000:
                score -= 15
            
            # Vitamins and minerals - higher is better
            vitamin_c = row.get('VitaminC', 0)
            if vitamin_c >= 50:
                score += 10
            elif vitamin_c >= 10:
                score += 5
            
            calcium = row.get('Calcium', 0)
            if calcium >= 200:
                score += 8
            elif calcium >= 100:
                score += 4
            
            iron = row.get('Iron', 0)
            if iron >= 5:
                score += 8
            elif iron >= 2:
                score += 4
            
            potassium = row.get('Potassium', 0)
            if potassium >= 300:
                score += 8
            elif potassium >= 150:
                score += 4
            
            # Ensure score is within 0-100 range
            score = max(0, min(100, score))
            scores.append(score)
        
        return np.array(scores)
    
    def _preprocess_data(self, df):
        """Clean and prepare data for training/prediction"""
        # Create a copy to avoid modifying original data
        data = df.copy()
        
        # Select only the features we need
        features = data[self.feature_columns].copy()
        
        # Handle missing values by filling with median
        features = features.fillna(features.median())
        
        # Remove extreme outliers (values beyond 99th percentile)
        for col in features.columns:
            q99 = features[col].quantile(0.99)
            features[col] = features[col].clip(upper=q99)
        
        return features
    
    def load_and_prepare_data(self, data_path, use_full_dataset=True):
        """Load USDA data and prepare for training"""
        print(f"Loading USDA data from {data_path}...")
        
        # Load the complete USDA dataset
        if use_full_dataset:
            df = pd.read_csv(data_path)
            print(f"Loaded complete dataset: {len(df)} records")
        else:
            # Load sample for testing
            df = pd.read_csv(data_path, nrows=1000)
            print(f"Loaded sample dataset: {len(df)} records")
        
        # Filter for records with required nutrition data
        df_clean = df[self.feature_columns + ['Description']].dropna()
        
        print(f"After cleaning: {len(df_clean)} records with complete data")
        
        # Prepare features and target (calculate health scores)
        X = self._preprocess_data(df_clean)
        y = self._calculate_health_score(df_clean)
        
        return X, y
    
    def train(self, data_path, test_size=0.2, use_full_dataset=True):
        """Train the health scoring model using USDA data"""
        print("Starting model training on USDA dataset...")
        
        # Load and prepare data
        X, y = self.load_and_prepare_data(data_path, use_full_dataset)
        
        if len(X) < 100:
            print("Warning: Very few training samples available")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"  R² Score: {r2:.3f}")
        print(f"  RMSE: {np.sqrt(mse):.3f}")
        print(f"  Training samples: {len(X_train)}")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nFeature Importance:")
        print(importance)
        
        self.is_trained = True
        return {'r2': r2, 'rmse': np.sqrt(mse), 'feature_importance': importance}
    
    def predict_health_score(self, nutrition_data):
        """
        Predict health score for given nutrition data
        
        Args:
            nutrition_data: dict or DataFrame with nutrition values per 100g
                Required keys: energy-kcal_100g, fat_100g, saturated-fat_100g,
                              sugars_100g, fiber_100g, proteins_100g, sodium_100g
        
        Returns:
            Health score (0-100) where higher is healthier
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Convert to DataFrame if dict
        if isinstance(nutrition_data, dict):
            df = pd.DataFrame([nutrition_data])
        else:
            df = nutrition_data.copy()
        
        # Preprocess data
        X = self._preprocess_data(df)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        scores = self.model.predict(X_scaled)
        
        # Ensure scores are within 0-100 range
        scores = np.clip(scores, 0, 100)
        
        return scores[0] if len(scores) == 1 else scores
    
    def get_health_rating(self, score):
        """Convert numeric score to descriptive rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 45:
            return "OK"
        else:
            return "Poor"
    
    def save_model(self, model_dir='models'):
        """Save trained model and scaler"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, 'health_score_model.pkl')
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
    
    def load_model(self, model_dir='models'):
        """Load pre-trained model and scaler"""
        model_path = os.path.join(model_dir, 'health_score_model.pkl')
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model files not found. Train the model first.")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.is_trained = True
        
        print("Model loaded successfully")

# Example usage
if __name__ == "__main__":
    # Initialize model
    model = HealthScoreModel()
    
    # Train model using USDA dataset
    data_path = "data/raw/USDA.csv"
    if os.path.exists(data_path):
        results = model.train(data_path, use_full_dataset=True)
        model.save_model()
        
        # Example prediction
        sample_nutrition = {
            'Calories': 250,
            'Protein': 8,
            'TotalFat': 10,
            'Carbohydrate': 30,
            'SaturatedFat': 3,
            'Sugar': 15,
            'Sodium': 400,
            'Calcium': 100,
            'Iron': 2,
            'Potassium': 200,
            'VitaminC': 10,
            'VitaminE': 1,
            'VitaminD': 0
        }
        
        score = model.predict_health_score(sample_nutrition)
        rating = model.get_health_rating(score)
        
        print(f"\nExample prediction:")
        print(f"Health Score: {score:.1f}/100")
        print(f"Rating: {rating}")
    else:
        print(f"Data file not found at {data_path}")
