"""
Simple ML model for demonstration
Uses Iris dataset for classification
"""
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IrisModel:
    """Iris classification model"""
    
    def __init__(self):
        self.model = None
        self.accuracy = None
        self.class_names = ['setosa', 'versicolor', 'virginica']
    
    def train(self):
        """Train the model"""
        logger.info("Loading Iris dataset...")
        iris = load_iris()
        X, y = iris.data, iris.target
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model trained with accuracy: {self.accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=self.class_names))
        
        return self.accuracy
    
    def predict(self, features):
        """Make prediction"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        features_array = np.array(features).reshape(1, -1)
        prediction = self.model.predict(features_array)[0]
        probabilities = self.model.predict_proba(features_array)[0]
        
        return {
            'prediction': int(prediction),
            'class_name': self.class_names[prediction],
            'probabilities': {
                name: float(prob) 
                for name, prob in zip(self.class_names, probabilities)
            }
        }
    
    def save(self, path='iris_model.joblib'):
        """Save model to disk"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        joblib.dump({
            'model': self.model,
            'accuracy': self.accuracy,
            'class_names': self.class_names
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path='iris_model.joblib'):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.accuracy = data['accuracy']
        self.class_names = data['class_names']
        logger.info(f"Model loaded from {path}")
        logger.info(f"Model accuracy: {self.accuracy:.4f}")

if __name__ == "__main__":
    # Train and save model
    model = IrisModel()
    model.train()
    model.save('iris_model.joblib')
    
    # Test prediction
    test_features = [5.1, 3.5, 1.4, 0.2]
    result = model.predict(test_features)
    logger.info(f"\nTest prediction: {result}")