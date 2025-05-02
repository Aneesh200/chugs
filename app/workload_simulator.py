import requests
import time
import random
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# API endpoints to test
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/analytics",
    "/api/nonexistent",  # Will cause 404 errors
    "/api/error"         # Will cause 500 errors
]

# Base URL of the API
BASE_URL = "http://localhost:8000"

def simulate_error():
    """Simulate different types of errors"""
    error_type = random.choice(['timeout', 'invalid_data', 'server_error'])
    
    if error_type == 'timeout':
        # Simulate timeout by using a very short timeout
        return requests.get(f"{BASE_URL}/api/users", timeout=0.001)
    elif error_type == 'invalid_data':
        # Send invalid JSON data
        return requests.post(f"{BASE_URL}/api/orders", data="invalid json")
    else:
        # Request non-existent endpoint
        return requests.get(f"{BASE_URL}/api/error")

def simulate_request():
    """Simulate a random API request with occasional errors"""
    endpoint = random.choice(ENDPOINTS)
    method = "GET" if endpoint != "/api/orders" else "POST"
    
    # 20% chance of simulating an error
    if random.random() < 0.2:
        try:
            response = simulate_error()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {str(e)}")
            return
    else:
        try:
            start_time = time.time()
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                # Add random delay to simulate processing time
                time.sleep(random.uniform(0.1, 0.5))
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            process_time = time.time() - start_time
            
            # Log with more details
            logging.info(
                f"Request: {method} {endpoint} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.2f}s"
            )
            
        except Exception as e:
            logging.error(f"Error making request to {endpoint}: {str(e)}")

def main():
    """Main function to run the workload simulator"""
    logging.info("Starting workload simulator...")
    
    try:
        while True:
            simulate_request()
            # Random delay between requests (0.1 to 2 seconds)
            # Occasionally add longer delays to simulate traffic spikes
            if random.random() < 0.1:  # 10% chance of longer delay
                time.sleep(random.uniform(2, 5))
            else:
                time.sleep(random.uniform(0.1, 2))
            
    except KeyboardInterrupt:
        logging.info("Workload simulator stopped by user")

if __name__ == "__main__":
    main() 