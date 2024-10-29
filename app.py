from fastapi import FastAPI, Request
from pydantic import BaseModel

from orderService.main import createOrder, rollbackOrder
from paymentService.main import processPayment, rollbackPayment
from shippingService.main import delivery

class Transaction(BaseModel):
    customer_name: str
    list_of_items: list[str]
    sender_bank_number: str
    address: str

app = FastAPI()

@app.post("/createOrder")
async def create_order(transaction: Transaction):
    service_stack = []
    orderData = {
        "customer_name": transaction.customer_name,
        "list_of_items": transaction.list_of_items,
    }
    orderResponse = createOrder(orderData)

    print("Order created sucessfully!!!")
    print("Order status: ", orderResponse['status'])
    
    if (orderResponse["status"] == "error"):
        return orderResponse

    order_service = {
        "name": "order",
        "data": orderResponse
    }
    service_stack.append(order_service)

    paymentData = {
        "sender_bank_number": transaction.sender_bank_number,
        "total_cost": orderResponse["total_cost"],
        "order_id": orderResponse["order_id"]
    }

    paymentResponse = processPayment(paymentData)

    print("Payment successfully!!!")
    print("Payment status: ", paymentResponse["status"])

    if (paymentResponse["status"] == "error"):
        return rollback_services(service_stack)

    payment_service = {
        "name": "payment",
        "data": paymentData
    }
    service_stack.append(payment_service)


    packetData = {
        "order_id": orderResponse["order_id"],
        "address": transaction.address,
    }
    deliveryResponse = delivery(packetData)

    if (deliveryResponse["status"] == "error"):
        return rollback_services(service_stack)

    return {
        "status": "success",
        "message": "Order placed successfully",
    }


def rollback_services(service_task):
    while service_task:
        service = service_task.pop()
        if service["name"] == "payment":
            rollbackPayment(service["data"])
        elif service["name"] == "order":
            rollbackOrder(service["data"]["order_id"])

    return {"status": "error", "message": "Transaction failed"}