from kafka import KafkaConsumer
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/log_analytics')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Log model
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime)
    method = Column(String)
    path = Column(String)
    status_code = Column(Integer)
    process_time = Column(Float)
    client_ip = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

def process_log(log_data):
    """Process and store log data in the database"""
    session = SessionLocal()
    try:
        log = Log(
            timestamp=datetime.fromisoformat(log_data['timestamp']),
            method=log_data['method'],
            path=log_data['path'],
            status_code=log_data['status_code'],
            process_time=log_data['process_time'],
            client_ip=log_data['client_ip']
        )
        session.add(log)
        session.commit()
    except Exception as e:
        print(f"Error processing log: {str(e)}")
        session.rollback()
    finally:
        session.close()

def main():
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        'api_logs',
        bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='log_processor_group'
    )

    print("Starting log consumer...")
    
    try:
        for message in consumer:
            log_data = message.value
            print(f"Processing log: {log_data}")
            process_log(log_data)
            
    except KeyboardInterrupt:
        print("Log consumer stopped by user")
    finally:
        consumer.close()

if __name__ == "__main__":
    main() 