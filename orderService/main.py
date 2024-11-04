# Connect to the Postgres database
import psycopg2
import dotenv
import os
import random

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

def createOrder(json_data):
    conn = connect()
    try:
        cursor = conn.cursor()
        
        #add code to demo error
        if json_data["customer_name"] == "TestError":
            raise Exception("Intentional failure: Invalid customer name for testing")
                            

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
    
def rollbackOrder(order_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        # conn.autocommit = False
        cursor.execute("UPDATE orders SET status = FALSE WHERE id = %s", (order_id,))
        conn.commit()
        cursor.close()
        return {"status": "success", "message": "Order rolled back successfully"}
    except Exception as e:
        conn.rollback()
        cursor.close()
        return {"status": "error", "message": "Order rollback failed", "error": str(e)}


        
