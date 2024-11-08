# Connect to the Postgres database
import psycopg2
import dotenv
import os
import random
import json

from kafka import KafkaProducer, KafkaConsumer

def connect():
    # DB_NAME = os.getenv("DB_NAME")
    # DB_USER = os.getenv("DB_USER")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    # DB_HOST = os.getenv("DB_HOST")

    DB_HOST='localhost'
    DB_USER='order_user'
    DB_PASSWORD='12345678'
    DB_NAME='order_db'

    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'order-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    group_id='order-group',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def createOrder(json_data):
    conn = connect()

    try:
        cursor = conn.cursor()

        total_cost = 0
        for item in json_data["list_of_items"]:
            cost = random.randint(1, 100)
            total_cost += cost

        cursor.execute(
            "INSERT INTO orders (customer_name, list_of_items, total, status) VALUES (%s, %s, %s, %s)",
            (json_data["customer_name"], json_data["list_of_items"], total_cost, True)
        )

        conn.commit()

        # Get the ID of the newly created order
        cursor.execute("SELECT MAX(id) FROM orders")
        order_id = cursor.fetchone()[0]

        cursor.close()
        return {"status": "success", "message": "Order created successfully", "total_cost": total_cost, "order_id": order_id}
    except Exception as e:
        return {"status": "error", "message": "Order creation failed", "error": str(e)}
    
def rollback(order_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status = %s WHERE id = %s",
        (False, order_id)
    )

    conn.commit()
    cursor.close()

    return {"status": "success", "message": "Order creation failed"}

if __name__ == "__main__":
    for delivery in consumer:
        message = delivery.value

        if (message["action"] == "Create order"):
            response = createOrder(message)

            if (response["status"] == "success"):
                response["action"] = "Create payment"
                response["sender_bank_number"] = message["sender_bank_number"]
                producer.send('payment-topic', value=response)
            elif (response["status"] == "error"):
                response["action"] = "Rollback main"
                producer.send('main-topic', value=response)
        
        elif (message["action"] == "Rollback order"):
            rollback(message["order_id"])
            
            response = {
                "status": "error",
                "message": "Order creation failed",
                "error": "Payment processing failed"
            }
            producer.send('main-topic', value=response)