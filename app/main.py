from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

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
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status', 'error_type']
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
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
        logger.info(
            f"Request: {request.method} {request.url.path} - Status: {response.status_code} - "
            f"Process Time: {process_time:.3f}s - Client IP: {request.client.host}"
        )
        
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
                status=response.status_code,
                error_type=type(Exception(response.status_code)).__name__
            ).inc()
            logger.error(f"Error occurred: {request.method} {request.url.path} - Status: {response.status_code}")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        
        # Record error metrics
        error_type = type(e).__name__
        status = 500 if not isinstance(e, HTTPException) else e.status_code
        
        ERROR_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status,
            error_type=error_type
        ).inc()
        
        # Log error to Kafka
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.url.path,
            'status_code': status,
            'process_time': process_time,
            'client_ip': request.client.host,
            'error': str(e)
        }
        kafka_producer.send('api_logs', value=log_data)
        
        raise

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
    # Simulate occasional slow response
    if time.time() % 10 < 2:  # 20% chance of slow response
        time.sleep(2)
    return {"users": ["user1", "user2", "user3"]}

@app.get("/api/products")
async def get_products():
    # Simulate occasional error
    if time.time() % 15 < 3:  # 20% chance of error
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"products": ["product1", "product2", "product3"]}

@app.post("/api/orders")
async def create_order():
    # Simulate processing time
    time.sleep(0.5)
    return {"order_id": "123", "status": "created"}

@app.get("/api/analytics")
async def get_analytics():
    # Simulate data processing
    time.sleep(0.3)
    return {"metrics": {"users": 100, "orders": 50}}

@app.get("/api/error")
async def trigger_error():
    raise HTTPException(status_code=500, detail="Simulated server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 