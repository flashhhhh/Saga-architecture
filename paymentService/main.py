# Connect to the Postgres database
import psycopg2
import dotenv
import os
import json

from kafka import KafkaProducer, KafkaConsumer

def connect():
    # dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    # dotenv.load_dotenv(dotenv_path)
    
    # DB_NAME = os.getenv("DB_NAME")
    # DB_USER = os.getenv("DB_USER")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    # DB_HOST = os.getenv("DB_HOST")

    DB_HOST='localhost'
    DB_USER='payment_user'
    DB_PASSWORD='12345678'
    DB_NAME='payment_db'

    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

conn = connect()
admin_bank_number = '0123456789'

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'payment-topic',
    bootstrap_servers='localhost:9092',
    group_id='payment-group',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def processPayment(json_data):
    # Start an ACID transaction
    # conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Check if the sender bank number is valid
        cursor.execute(
            "SELECT * FROM bank_accounts WHERE bank_number = %s",
            (json_data["sender_bank_number"],)
        )
        sender = cursor.fetchone()

        if sender is None:
            raise Exception("Invalid sender bank number")

        # Check if the sender has enough balance
        if int(sender[0]) < int(json_data["total_cost"]):
            raise Exception("Insufficient balance")

        # Deduct the total cost from the sender's account
        cursor.execute(
            "UPDATE bank_accounts SET balance = balance - %s WHERE bank_number = %s",
            (json_data["total_cost"], json_data["sender_bank_number"])
        )

        # Add the total cost to the admin's account
        cursor.execute(
            "UPDATE bank_accounts SET balance = balance + %s WHERE bank_number = %s",
            (json_data["total_cost"], admin_bank_number)
        )

        # Add to transaction history
        cursor.execute(
            "INSERT INTO transaction_history (sender_bank_number, receiver_bank_number, amount) VALUES (%s, %s, %s)",
            (json_data["sender_bank_number"], admin_bank_number, json_data["total_cost"])
        )

        conn.commit()

        # Get the last transaction ID
        cursor.execute("SELECT MAX(id) FROM transaction_history")
        transaction_id = cursor.fetchone()[0]
        cursor.close()

        return {"status": "success", "message": "Payment processed successfully", "transaction_id": transaction_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        return {"status": "error", "message": "Payment processing failed", "error": str(e)}

def rollbackPayment(transaction_id):
    cursor = conn.cursor()
    print(transaction_id)

    try:
        # Get the transaction details
        cursor.execute(
            "SELECT sender_bank_number, amount FROM transaction_history WHERE id = %s",
            (transaction_id,)
        )
        transaction = cursor.fetchone()

        print(transaction)

        # Deduct the total cost from the admin's account
        cursor.execute(
            "UPDATE bank_accounts SET balance = balance - %s WHERE bank_number = %s",
            (transaction[1], admin_bank_number)
        )

        # Add the total cost to the sender's account
        cursor.execute(
            "UPDATE bank_accounts SET balance = balance + %s WHERE bank_number = %s",
            (transaction[1], transaction[0])
        )

        print(admin_bank_number, transaction[0], transaction[1])

        # Add to transaction history
        cursor.execute(
            "INSERT INTO transaction_history (sender_bank_number, receiver_bank_number, amount) VALUES (%s, %s, %s)",
            (admin_bank_number, transaction[0], transaction[1])
        )

        conn.commit()
        cursor.close()

        return {"status": "success", "message": "Payment rolled back successfully"}
    except Exception as e:
        conn.rollback()
        cursor.close()

        return {"status": "error", "message": "Payment rollback failed", "error": str(e)}

if __name__ == "__main__":
    for delivery in consumer:
        message = delivery.value

        if (message["action"] == "Create payment"):
            response = processPayment(message)

            if (response["status"] == "success"):
                response["action"] = "Create shipping"
                response["order_id"] = message["order_id"]
                producer.send('shipping-topic', value=response)
            elif (response["status"] == "error"):
                response["action"] = "Rollback order"
                response["order_id"] = message["order_id"]
                producer.send('order-topic', value=response)

        elif (message["action"] == "Rollback payment"):
            response = rollbackPayment(message["transaction_id"])

            if (response["status"] == "success"):
                response["status"] = "error"
                response["action"] = "Rollback order"
                response["order_id"] = message["order_id"]
                producer.send('order-topic', value=response)
            elif (response["status"] == "error"):
                # When saga rollback fails, we need to manually rollback the payment
                manually = True
                print(response)