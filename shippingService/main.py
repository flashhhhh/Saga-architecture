def delivery(packet):
    OK = int(input())
    if OK:  
        return {
            "status": "success",
            "message": "Order delivered successfully",
        }
    else:
        return {
            "status": "error",    
            "message": "Order delivered error",
        }
    

