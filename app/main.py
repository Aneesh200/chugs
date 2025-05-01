from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Log Analytics Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Kafka producer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Create log entry
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": process_time,
        "client_ip": request.client.host
    }

    # Log to stdout (will be captured by Promtail)
    log_level = logging.INFO  # Default log level

    if response.status_code >= 500:
        log_level = logging.ERROR
    elif response.status_code >= 400:
        log_level = logging.WARNING

    log_message = (
        f"Request: {request.method} {request.url.path} - Status: {response.status_code} - "
        f"Process Time: {process_time:.3f}s - Client IP: {request.client.host}"
    )

    logger.log(log_level, log_message)

    # Send log to Kafka
    kafka_producer.send('api_logs', value=log_entry)

    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)

    if response.status_code >= 400:
        ERROR_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        logger.error(f"Error occurred: {request.method} {request.url.path} - Status: {response.status_code}")

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "Welcome to Log Analytics Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/users")
async def get_users():
    logger.info("Fetching user list.") # Example INFO log
    return {"users": ["user1", "user2", "user3"]}

@app.get("/api/products")
async def get_products():
    if random.random() < 0.1:  # Simulate occasional warning
        logger.warning("Product list is getting long. Consider pagination.")
    return {"products": ["product1", "product2", "product3"]}

@app.post("/api/orders")
async def create_order():
    if random.random() < 0.05:  # Simulate occasional order creation failure
        logger.error("Order creation failed due to inventory issues.")
        raise HTTPException(status_code=500, detail="Order creation failed") # Propagate error
    return {"order_id": "123", "status": "created"}

@app.get("/api/analytics")
async def get_analytics():
    return {"metrics": {"visitors": 100, "orders": 50}}

@app.get("/api/notifications")
async def get_notifications():
    logger.info("Fetching notifications...")
    return {"notifications": ["Notification 1", "Notification 2"]}

@app.get("/api/settings")
async def get_settings():
    try:
        # Simulate reading settings from a file (potential for error)
        with open("config.json", "r") as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        logger.warning("Config file not found. Using default settings.")
        return {"theme": "default", "language": "en"}
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        raise HTTPException(status_code=500, detail="Failed to load settings")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)