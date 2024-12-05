# Saga chroreography demo

This branch shows the implementation of choreography saga pattern in microservices using Apache Kafka as a message broker to communicate between services.

## Project architecture
- Order service: This service is used for creating new orders and updating order status.
- Payment service: This service is used for online paying money.
- Shipping service: This service is used for updating shipping status.

### Flow 
```
[Request] -> [API Server] -> [Order Service] -> [Payment Service] -> [Shipping Service] -> [API Server] -> [Response]
```

## Key features
- Compensating failure distributed transaction by using roll back technique.
- Message queue fault tolerance.

## Prerequisites
- Python
- FastAPI
- Apache Kafka
- PostgreSQL

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/flashhhhh/Saga-architecture.git
cd Saga-architecture
git checkout choreography-saga
```

2. **Install Apache Kafka**
https://kafka.apache.org/downloads

You should have a folder named **kafka_2.x-x.x.x** after installation.

3. **Create PostgreSQL database management system**
https://www.postgresql.org/download/

4. Create virtual env with Python
```bash
python -m venv venv
source venv/bin/activate
```

5. Install Python libraries
```bash
pip install -r requirements.txt
```

## Running the application

### 1. Start kafka server
```bash
cd $KAFKA_DIR

bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

### 2. Start PostgreSQL server and create databases
#### Firstly, launch the PostgreSQL server
```bash
sudo systemctl start postgresql
```

#### Next, create 2 databases corresponding to 2 services
##### Order service:
```bash
psql -U postgres -d order_db < orderService/script.sql
```

##### Payment service:
```bash
psql -U postgres -d payment_db < paymentService/script.sql
```

### 3. Launch all of the services 
#### Create a new terminal, then run
```bash
cd orderService/
python main.py
```

#### Create another terminal, then run
```bash
cd paymentService/
python main.py
```

#### Create the third terminal, then run
#### Create a new terminal, then run
```bash
cd shippingService/
python main.py
```

### 4. Launch the backend server
```bash
uvicorn app:app --port 8000 --reload
```

Now you can access the server through: http://localhost:8000/docs

## Interacting with the backend server
