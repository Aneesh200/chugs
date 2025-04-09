from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import json
from datetime import datetime
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

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
    
    # Send log to Kafka
    kafka_producer.send('api_logs', value=log_entry)
    
    return response

@app.get("/")
async def root():
    return {"message": "Welcome to Log Analytics Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/users")
async def get_users():
    return {"users": ["user1", "user2", "user3"]}

@app.get("/api/products")
async def get_products():
    return {"products": ["product1", "product2", "product3"]}

@app.post("/api/orders")
async def create_order():
    return {"order_id": "123", "status": "created"}

@app.get("/api/analytics")
async def get_analytics():
    return {"metrics": {"visitors": 100, "orders": 50}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 