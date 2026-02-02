"""
Load testing script to trigger auto-scaling
"""
import requests
import concurrent.futures
import time
import numpy as np
from datetime import datetime

BASE_URL = "http://localhost:8080"

def send_request():
    """Send single prediction request"""
    payload = {"features": list(np.random.randn(4))}
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            timeout=5
        )
        latency = (time.time() - start) * 1000
        
        return {
            "success": response.status_code == 200,
            "latency": latency,
            "status": response.status_code
        }
    except Exception as e:
        return {
            "success": False,
            "latency": 0,
            "error": str(e)
        }

def load_test(num_requests=1000, workers=20):
    """Run load test"""
    print("=" * 70)
    print(f"LOAD TEST: {num_requests} requests with {workers} concurrent workers")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_request) for _ in range(num_requests)]
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            completed += 1
            
            if completed % 100 == 0:
                print(f"Progress: {completed}/{num_requests} requests completed")
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = sum(1 for r in results if r["success"])
    failed = num_requests - successful
    latencies = [r["latency"] for r in results if r["success"]]
    
    print()
    print("=" * 70)
    print("LOAD TEST RESULTS")
    print("=" * 70)
    print(f"Total Requests: {num_requests}")
    print(f"Successful: {successful} ({successful/num_requests*100:.2f}%)")
    print(f"Failed: {failed} ({failed/num_requests*100:.2f}%)")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Requests/sec: {num_requests/total_time:.2f}")
    print()
    print("Latency Statistics:")
    print(f"  Mean: {np.mean(latencies):.2f}ms")
    print(f"  Median: {np.median(latencies):.2f}ms")
    print(f"  P95: {np.percentile(latencies, 95):.2f}ms")
    print(f"  P99: {np.percentile(latencies, 99):.2f}ms")
    print(f"  Min: {np.min(latencies):.2f}ms")
    print(f"  Max: {np.max(latencies):.2f}ms")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    print("\n🚀 Starting load test to trigger auto-scaling...\n")
    
    # Run multiple waves to see scaling
    for wave in range(3):
        print(f"\n📊 WAVE {wave + 1}/3\n")
        load_test(num_requests=500, workers=30)
        
        if wave < 2:
            print("\n⏳ Waiting 30 seconds before next wave...\n")
            time.sleep(30)
    
    print("\n✅ Load test complete!")
    print("\nCheck pod scaling with:")
    print("  kubectl get pods -n ml-system --watch")
    print("  kubectl get hpa -n ml-system --watch")