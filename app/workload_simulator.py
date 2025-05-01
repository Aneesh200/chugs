import requests
import time
import random
from datetime import datetime
import logging

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
    "/api/notifications",
    "/api/settings"
]

# Base URL of the API
BASE_URL = "http://localhost:8000"

def simulate_request():
    """Simulate a random API request"""
    endpoint = random.choice(ENDPOINTS)
    method = "GET" if endpoint not in ["/api/orders", "/api/settings"] else "POST"  # /api/settings also performs file reading, should be a get as well

    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        else:  # method == "POST"
            # Added a payload for the /api/orders endpoint to simulate data
            payload = {"item": "widget", "quantity": random.randint(1, 5)}
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload)  # Send JSON data

        process_time = time.time() - start_time

        logging.info(
            f"Request: {method} {endpoint} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}s"
        )
        if response.status_code >= 400:  # Log failed requests too
            logging.error(f"Request failed with status code: {response.status_code}")


    except requests.exceptions.RequestException as e:  # Catch connection errors, etc.
        logging.error(f"Error making request to {endpoint}: {str(e)}")
    except Exception as e:  # Catch all other exceptions, just in case
        logging.error(f"Unexpected error: {str(e)}")

def main():
    """Main function to run the workload simulator"""
    logging.info("Starting workload simulator...")

    try:
        while True:
            simulate_request()
            # Random delay between requests (0.1 to 2 seconds)
            time.sleep(random.uniform(0.1, 2))

    except KeyboardInterrupt:
        logging.info("Workload simulator stopped by user")

if __name__ == "__main__":
    main()