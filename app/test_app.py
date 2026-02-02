"""
Test script for the API
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("TESTING HEALTH ENDPOINT")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_ready():
    """Test readiness endpoint"""
    print("=" * 60)
    print("TESTING READINESS ENDPOINT")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/ready")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_info():
    """Test info endpoint"""
    print("=" * 60)
    print("TESTING INFO ENDPOINT")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_predict():
    """Test prediction"""
    print("=" * 60)
    print("TESTING PREDICT ENDPOINT")
    print("=" * 60)
    
    # Iris setosa
    payload = {
        "features": [5.1, 3.5, 1.4, 0.2]
    }
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    latency = (time.time() - start) * 1000
    
    print(f"Status: {response.status_code}")
    print(f"Latency: {latency:.2f}ms")
    print(json.dumps(response.json(), indent=2))
    print()

def test_batch_predict():
    """Test batch prediction"""
    print("=" * 60)
    print("TESTING BATCH PREDICT ENDPOINT")
    print("=" * 60)
    
    payload = {
        "batch": [
            [5.1, 3.5, 1.4, 0.2],  # setosa
            [6.7, 3.0, 5.2, 2.3],  # virginica
            [5.9, 3.0, 4.2, 1.5]   # versicolor
        ]
    }
    
    response = requests.post(f"{BASE_URL}/batch-predict", json=payload)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def load_test():
    """Simple load test"""
    print("=" * 60)
    print("LOAD TEST (100 requests)")
    print("=" * 60)
    
    latencies = []
    payload = {"features": [5.1, 3.5, 1.4, 0.2]}
    
    for i in range(100):
        start = time.time()
        response = requests.post(f"{BASE_URL}/predict", json=payload)
        latencies.append((time.time() - start) * 1000)
        
        if (i + 1) % 20 == 0:
            print(f"Progress: {i + 1}/100")
    
    import numpy as np
    print(f"\nLatency Statistics:")
    print(f"  Mean: {np.mean(latencies):.2f}ms")
    print(f"  Median: {np.median(latencies):.2f}ms")
    print(f"  P95: {np.percentile(latencies, 95):.2f}ms")
    print(f"  P99: {np.percentile(latencies, 99):.2f}ms")
    print(f"  Min: {np.min(latencies):.2f}ms")
    print(f"  Max: {np.max(latencies):.2f}ms")
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ML MODEL API - COMPREHENSIVE TESTING")
    print("=" * 60 + "\n")
    
    test_health()
    test_ready()
    test_info()
    test_predict()
    test_batch_predict()
    load_test()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)