#!/usr/bin/env python3
"""Cancel all pending orders"""
import requests
import json

ACCOUNT_ID = "001-003-8520002-001"
API_KEY = "8d4ff0fbea2b109c515a956784596208-be028efcd5faae816357345ff32c3bac"
BASE_URL = "https://api-fxtrade.oanda.com/v3"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Get pending orders
response = requests.get(
    f"{BASE_URL}/accounts/{ACCOUNT_ID}/pendingOrders",
    headers=headers
)

if response.status_code == 200:
    orders = response.json()
    print(f"Found {len(orders.get('orders', []))} pending orders")
    
    for order in orders.get('orders', []):
        order_id = order['id']
        cancel_response = requests.put(
            f"{BASE_URL}/accounts/{ACCOUNT_ID}/orders/{order_id}/cancel",
            headers=headers
        )
        if cancel_response.status_code == 200:
            print(f"✅ Cancelled order {order_id}")
        else:
            print(f"❌ Failed to cancel {order_id}: {cancel_response.text}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
