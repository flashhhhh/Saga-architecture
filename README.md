# Saga orchestration demo

This branch shows the implementation of orchestration saga pattern in microservices where the saga orchestrator handles all the transactions and tells the services which operation to perform based on events.

## Project architecture
- Order service: This service is used for creating new orders and updating order status.
- Payment service: This service is used for online paying money.
- Shipping service: This service is used for updating shipping status.

### Flow 
```
[Request] -> [Orchestrator] -> [Order Service]-> [Orchestrator] -> [Payment Service]-> [Orchestrator] -> [Shipping Service] -> [Orchestrator] -> [Response]
```

## Key features
- The orchestrator executes saga requests, stores and interprets the states of each task, and handles failure recovery with compensating transactions.

## Prerequisites
- Python
- FastAPI
- PostgreSQL

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/flashhhhh/Saga-architecture.git
cd Saga-architecture
git checkout orchestration-saga
```

2. **Create PostgreSQL database management system**
https://www.postgresql.org/download/

3. **Create virtual env with Python**
```bash
pip install virtualenv
virtualenv --python C:\Path\To\Python\python.exe venv
.\venv\Scripts\activate
```

4. Install Python libraries
```bash
pip install -r requirements.txt
```

## Running the application
### 1. Start PostgreSQL server and create databases
#### Create 2 databases corresponding to 2 services

##### Order service:

```bash
psql -U postgres -d order_db < orderService\script.sql
```

##### Payment service:

```bash
psql -U postgres -d payment_db < paymentService\script.sql
```

### 2. Launch the backend server
```bash
uvicorn app:app --port 8000 --reload
```

Now you can access the server through: http://localhost:8000/docs
