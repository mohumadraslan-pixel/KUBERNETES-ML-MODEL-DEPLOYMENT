"""
Flask API for ML model serving
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import logging
import time
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Prometheus metrics
prediction_counter = Counter(
    'ml_predictions_total',
    'Total number of predictions',
    ['model', 'class']
)
prediction_duration = Histogram(
    'ml_prediction_duration_seconds',
    'Time spent processing prediction'
)
model_accuracy = Gauge(
    'ml_model_accuracy',
    'Model accuracy score'
)
active_requests = Gauge(
    'ml_active_requests',
    'Number of active requests'
)
error_counter = Counter(
    'ml_errors_total',
    'Total number of errors',
    ['type']
)

# Load model
MODEL_PATH = os.getenv('MODEL_PATH', 'iris_model.joblib')

try:
    logger.info(f"Loading model from {MODEL_PATH}...")
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    model_accuracy_value = model_data['accuracy']
    class_names = model_data['class_names']
    
    # Set accuracy gauge
    model_accuracy.set(model_accuracy_value)
    
    logger.info("✅ Model loaded successfully")
    logger.info(f"Model accuracy: {model_accuracy_value:.4f}")
    logger.info(f"Classes: {class_names}")
    
except Exception as e:
    logger.error(f"❌ Failed to load model: {e}")
    raise

# Track start time for uptime
start_time = time.time()

@app.before_request
def before_request():
    """Track active requests"""
    active_requests.inc()

@app.after_request
def after_request(response):
    """Decrease active requests counter"""
    active_requests.dec()
    return response

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'ML Model API',
        'version': '1.0.0',
        'model': 'Iris Classifier',
        'accuracy': f"{model_accuracy_value * 100:.2f}%",
        'endpoints': {
            'health': '/health',
            'ready': '/ready',
            'predict': '/predict',
            'batch_predict': '/batch-predict',
            'metrics': '/metrics',
            'info': '/info'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint (liveness probe)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/ready')
def ready():
    """Readiness check endpoint"""
    try:
        # Test model
        test_features = np.array([[5.1, 3.5, 1.4, 0.2]])
        _ = model.predict(test_features)
        
        return jsonify({
            'status': 'ready',
            'model_loaded': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503

@app.route('/info')
def info():
    """Model information"""
    uptime = time.time() - start_time
    
    return jsonify({
        'model': 'Random Forest Classifier',
        'dataset': 'Iris',
        'accuracy': model_accuracy_value,
        'classes': class_names,
        'features': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
        'uptime_seconds': uptime,
        'version': '1.0.0'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict endpoint"""
    start_pred = time.time()
    
    try:
        # Get input
        data = request.get_json()
        
        if 'features' not in data:
            error_counter.labels(type='invalid_input').inc()
            return jsonify({'error': 'Missing features field'}), 400
        
        features = data['features']
        
        if len(features) != 4:
            error_counter.labels(type='invalid_input').inc()
            return jsonify({
                'error': f'Expected 4 features, got {len(features)}'
            }), 400
        
        # Make prediction
        with prediction_duration.time():
            features_array = np.array(features).reshape(1, -1)
            prediction = model.predict(features_array)[0]
            probabilities = model.predict_proba(features_array)[0]
        
        class_name = class_names[prediction]
        
        # Update metrics
        prediction_counter.labels(model='iris', class=class_name).inc()
        
        processing_time = (time.time() - start_pred) * 1000
        
        result = {
            'prediction': int(prediction),
            'class': class_name,
            'probabilities': {
                name: float(prob)
                for name, prob in zip(class_names, probabilities)
            },
            'confidence': float(probabilities[prediction]),
            'processing_time_ms': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Prediction: {class_name} (confidence: {probabilities[prediction]:.4f})")
        
        return jsonify(result), 200
    
    except Exception as e:
        error_counter.labels(type='prediction_error').inc()
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """Batch prediction endpoint"""
    try:
        data = request.get_json()
        
        if 'batch' not in data:
            return jsonify({'error': 'Missing batch field'}), 400
        
        batch = data['batch']
        results = []
        
        for features in batch:
            if len(features) != 4:
                results.append({'error': f'Invalid feature count: {len(features)}'})
                continue
            
            features_array = np.array(features).reshape(1, -1)
            prediction = model.predict(features_array)[0]
            probabilities = model.predict_proba(features_array)[0]
            
            class_name = class_names[prediction]
            prediction_counter.labels(model='iris', class=class_name).inc()
            
            results.append({
                'prediction': int(prediction),
                'class': class_name,
                'confidence': float(probabilities[prediction])
            })
        
        return jsonify({
            'results': results,
            'count': len(results)
        }), 200
    
    except Exception as e:
        error_counter.labels(type='batch_error').inc()
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    error_counter.labels(type='internal_error').inc()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )