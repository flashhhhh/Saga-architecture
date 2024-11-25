import json

from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

consumer = KafkaConsumer(
    'shipping-topic',
    bootstrap_servers='localhost:9092',
    group_id='shipping-group',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def shipping(packet):
    ok = input("Press 'y' or 'n' to simulate shipping success or failure: ")

    if ok == 'y':
        return {
            "status": "success",
            "message": "Order delivered successfully",
        }
    else:
        return {
            "status": "error",
            "message": "Order delivery failed",
        }

if __name__ == "__main__":
    for delivery in consumer:
        message = delivery.value

        if (message["action"] == "Create shipping"):
            with open("../.log", "a") as f:
                f.write(f"Received request to create shipping\n")
            
            response = shipping(message)

            if (response["status"] == "success"):
                with open("../.log", "a") as f:
                    f.write(f"Shipping successful\n")
                
                producer.send('main-topic', value=response)
            elif (response["status"] == "error"):
                with open("../.log", "a") as f:
                    f.write(f"Shipping failed.\n")

                response["action"] = "Rollback payment"
                response["order_id"] = message["order_id"]
                response["transaction_id"] = message["transaction_id"]
                producer.send('payment-topic', value=response)