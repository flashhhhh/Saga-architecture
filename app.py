from fastapi import FastAPI, Request
from pydantic import BaseModel

from orderService.main import createOrder
from paymentService.main import processPayment
from shippingService.main import delivery

class Transaction(BaseModel):
    customer_name: str
    list_of_items: list[str]
    sender_bank_number: str
    address: str

app = FastAPI()

@app.post("/createOrder")
async def create_order(transaction: Transaction):
    orderData = {
        "customer_name": transaction.customer_name,
        "list_of_items": transaction.list_of_items,
    }
    response = createOrder(orderData)

    if (response["status"] == "error"):
        return response

    paymentData = {
        "sender_bank_number": transaction.sender_bank_number,
        "total_cost": response["total_cost"]
    }
    paymentResponse = processPayment(paymentData)

    if (paymentResponse["status"] == "error"):
        return paymentResponse

    packetData = {
        "order_id": response["order_id"],
        "address": transaction.address,
    }
    deliveryResponse = delivery(packetData)

    if (deliveryResponse["status"] == "error"):
        return deliveryResponse

    return {
        "status": "success",
        "message": "Order placed successfully",
    }