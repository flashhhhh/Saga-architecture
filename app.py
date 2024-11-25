from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

from kafka import KafkaProducer, KafkaConsumer

class Transaction(BaseModel):
    customer_name: str
    list_of_items: list[str]
    sender_bank_number: str
    address: str

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

consumer = KafkaConsumer(
    'main-topic',
    bootstrap_servers='localhost:9092',
    group_id='main-group',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

@app.post("/createOrder")
async def create_order(transaction: Transaction):
    with open(".log", "a") as f:
        f.write("----------------------------------------------------------\n")
        f.write(f"Received HTTP request\n")

    orderData = {
        "status": "success",
        "customer_name": transaction.customer_name,
        "list_of_items": transaction.list_of_items,
        "sender_bank_number": transaction.sender_bank_number,
        "action": "Create order"
    }

    producer.send('order-topic', value=orderData)
    
    # Receive only 1 response from orderService

    while True:
        for delivery in consumer:
            message = delivery.value
            
            if message["status"] == "success":
                with open(".log", "a") as f:
                    f.write(f"Received response from orderService\n")

                return {"status": "success", "message": "Order created successfully"}
            else:
                with open(".log", "a") as f:
                    f.write(f"Received response from orderService\n")

                return {"status": "error", "message": "Order creation failed"}

# if __name__ == "__main__":
#     for delivery in consumer:
#         message = delivery.value

#         # if (message["action"] )