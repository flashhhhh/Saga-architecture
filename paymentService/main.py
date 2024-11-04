# Connect to the Postgres database
import psycopg2
import dotenv
import os

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

def processPayment(json_data):
    # Start an ACID transaction
    cursor = conn.cursor()

    try:
        # conn.autocommit = False
        
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

        cursor.execute(
            "INSERT INTO transaction_history (sender_bank_number, receiver_bank_number, amount) VALUES (%s, %s, %s)",
            (json_data["sender_bank_number"], admin_bank_number, json_data["total_cost"])
        )

        conn.commit()

        # cursor.execute("SELECT * FROM bank_accounts")
        # print("After payment:", cursor.fetchall())
          # Get the last transaction ID
        cursor.execute("SELECT MAX(id) FROM transaction_history")
        transaction_id = cursor.fetchone()[0]
    
        cursor.close()
        # conn.autocommit = True
        return {"status": "success", "message": "Payment processed successfully", "transaction_id": transaction_id}
    except Exception as e:
        conn.rollback()
        cursor.close()
        return {"status": "error", "message": "Payment processing failed", "error": str(e)}

def rollbackPayment(transaction_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        # conn.autocommit = False
        cursor.execute(
            "SELECT sender_bank_number, amount FROM transaction_history WHERE id = %s",
            (transaction_id,)
        )
        transaction = cursor.fetchone()

        cursor.execute(
            "UPDATE bank_accounts SET balance = balance - %s WHERE bank_number = %s",
            (transaction[1], admin_bank_number)
        )

        cursor.execute(
            "UPDATE bank_accounts SET balance = balance + %s WHERE bank_number = %s",
            (transaction[1], transaction[0])
        )

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


        
        
    