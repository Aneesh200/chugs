# Log Analytics Platform

A real-time log analytics platform that collects, processes, and visualizes API logs using FastAPI, Kafka, PostgreSQL, and Grafana.

## Features

- Real-time log collection and processing
- API request monitoring
- Response time tracking
- Error tracking and visualization
- Beautiful Grafana dashboards

## Prerequisites

- Docker and Docker Compose
- Python 3.9 or higher (for local development)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd log-analytics-platform
```

2. Create a `.env` file in the root directory:
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/log_analytics
```

3. Start the services using Docker Compose:
```bash
docker-compose up -d
```

4. Access the services:
- API: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)
- PostgreSQL: localhost:5432
- Kafka: localhost:9092

## Components

1. **API Server** (`app/main.py`):
   - FastAPI application with sample endpoints
   - Middleware for log collection
   - Kafka producer for log streaming

2. **Workload Simulator** (`app/workload_simulator.py`):
   - Generates random API requests
   - Simulates real-world traffic

3. **Log Consumer** (`app/log_consumer.py`):
   - Kafka consumer for log processing
   - Stores logs in PostgreSQL

4. **Grafana Dashboards**:
   - Request Count per Endpoint
   - Response Time Trends
   - Error Rate Monitoring
   - Real-time Log Stream

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API server locally:
```bash
uvicorn app.main:app --reload
```

3. Run the workload simulator:
```bash
python app/workload_simulator.py
```

4. Run the log consumer:
```bash
python app/log_consumer.py
```

## Monitoring

1. Access Grafana at http://localhost:3000
2. Add PostgreSQL as a data source:
   - Host: postgres
   - Port: 5432
   - Database: log_analytics
   - User: postgres
   - Password: postgres

3. Import the following dashboards:
   - API Request Overview
   - Response Time Analysis
   - Error Monitoring
   - Real-time Log Stream

## License

MIT 