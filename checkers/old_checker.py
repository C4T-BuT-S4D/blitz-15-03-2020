#!/usr/bin/env python3
import base64
import json
import random
import re
import string
import sys
import uuid

import requests
from Crypto.Cipher import DES
from websocket import create_connection


def generator(size=12, chars=string.digits + string.ascii_letters):
    return ''.join(random.choice(chars) for _ in range(size))


def genflag(size=31, chars=string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size)) + '='


def pad(text):
    while len(text) % 8 != 0:
        text += b' '
    return text


cmd = sys.argv[1]


ip = re.search("([0-9]{1,3}[\.]){3}[0-9]{1,3}", sys.argv[2]).group(0)


port = 9090

OK, CORRUPT, MUMBLE, DOWN = 101, 102, 103, 104

CT = 5
RT = 5

url = 'ws://{}:{}/api/ws'.format(ip, port)


def close(code):
    print('Exit with code {}'.format(code), file=sys.stderr)
    exit(code)


def check():
    try:
        ws = create_connection(url, timeout=5)
        ws.close()
        exit(OK)
    except Exception as e:
        print(str(e))
        exit(DOWN)


def put():
    vuln = int(sys.argv[5])
    #vuln = 1
    if vuln == 1:
        s = requests.Session()
        username = str(uuid.uuid4())
        password = generator()

        name = str(uuid.uuid4())
        description = sys.argv[4]  # flag
        cost = 2147483647
        in_stock = 1000

        fake_name = str(uuid.uuid4())
        fake_description = generator(size=36)
        fake_cost = 1
        fake_in_stock = 10000

        try:
            response = s.post('http://{}:{}/api/register'.format(ip, port),
                              json={'username': username, 'password': password}, timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't register")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/login'.format(ip, port),
                              json={'username': username, 'password': password},
                              timeout=(CT, RT)).text
            if not 'User' in response:
                print("Can't login")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/add'.format(ip, port),
                              json={'name': name, 'description': description, 'cost': cost, 'in_stock': in_stock},
                              timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't add merch")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/add'.format(ip, port),
                              json={'name': fake_name, 'description': fake_description, 'cost': fake_cost,
                                    'in_stock': fake_in_stock},
                              timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't add merch")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        print(fake_name + ':' + fake_description + ':' + username + ':' + password + ':' + description)
        s.close()
        close(OK)

    elif vuln == 2:
        try:
            ws = create_connection(url, timeout=5)
            ws.recv()

            username = str(uuid.uuid4())
            comment = sys.argv[4]

            data = json.dumps(
                {'action': 'send_comment', 'data': {'username': username, 'comment': comment, 'private': 'TRUE'}})
            ws.send(data)

            response = ws.recv()
            if not 'ok' in response:
                print("Can't send comment")
                close(CORRUPT)
            print(username)
            ws.close()
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

    elif vuln == 3:
        try:
            ws = create_connection(url, timeout=5)
            ws.recv()

            username = str(uuid.uuid4())
            text = sys.argv[4]

            data = json.dumps(
                {'action': 'create_report', 'data': {'username': username, 'email': username, 'text': text}})
            ws.send(data)

            response = ws.recv()

            if not 'ok' in response:
                print("Can't create report")
                close(CORRUPT)
            ws.close()

            jsonResponse = json.loads(response)
            print(jsonResponse['Response']['object_id'] + ':' + jsonResponse['Response']['private_key'])
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

    elif vuln == 4:
        s = requests.Session()
        sender = str(uuid.uuid4())
        password = generator()

        value = 1
        msg = sys.argv[4]

        receiver = str(uuid.uuid4())
        receiver_password = generator()

        try:
            response = s.post('http://{}:{}/api/register'.format(ip, port),
                              json={'username': receiver, 'password': receiver_password}, timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't register")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/register'.format(ip, port),
                              json={'username': sender, 'password': password}, timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't register")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/login'.format(ip, port),
                              json={'username': sender, 'password': password},
                              timeout=(CT, RT)).text
            if not 'User' in response:
                print("Can't login")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/send'.format(ip, port),
                              json={'receiver': receiver, 'value': value, 'msg': msg}, timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't send money")
                close(CORRUPT)
            print(receiver + ':' + receiver_password)
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)


def get():
    vuln = int(sys.argv[5])
    if vuln == 1:
        s = requests.Session()
        username = str(uuid.uuid4())
        password = generator()

        arg = sys.argv[3].split(':')

        flag_name = arg[0]
        fake_flag = arg[1]
        merch_username = arg[2]
        merch_password = arg[3]
        flag = arg[4]

        try:
            response = s.post('http://{}:{}/api/register'.format(ip, port),
                              json={'username': username, 'password': password}, timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't register")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/login'.format(ip, port),
                              json={'username': username, 'password': password},
                              timeout=(CT, RT)).text
            if not 'User' in response:
                print("Can't login")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.post('http://{}:{}/api/buy'.format(ip, port), json={'name': flag_name},
                              timeout=(CT, RT)).text
            if not 'Ok' in response:
                print("Can't buy merch")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.get('http://{}:{}/api/get_orders'.format(ip, port), timeout=(CT, RT)).text

            if not fake_flag in response:
                print('Not bought merch description')
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        r = requests.Session()
        try:
            response = r.post('http://{}:{}/api/login'.format(ip, port),
                              json={'username': merch_username, 'password': merch_password},
                              timeout=(CT, RT)).text
            if not 'User' in response:
                print("Can't login")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = r.get('http://{}:{}/api/get_my_flags'.format(ip, port), timeout=(CT, RT)).text
            print(response)

            if not flag in response:
                print('Not my products description')
                close(CORRUPT)
            r.close()
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)


    elif vuln == 2:
        try:
            ws = create_connection(url, timeout=5)
            ws.recv()

            username = sys.argv[3]
            flag = sys.argv[4]

            data = json.dumps(
                {'action': 'get_my_comments', 'data': username})
            ws.send(data)

            response = ws.recv()
            if not flag in response:
                print('Not comments')
                close(CORRUPT)
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

    elif vuln == 3:
        try:
            ws = create_connection(url, timeout=5)
            ws.recv()

            arg = sys.argv[3].split(':')

            object_id = arg[0]
            private_key = arg[1].encode()
            flag = sys.argv[4]

            data = json.dumps(
                {'action': 'get_report', 'data': object_id})
            ws.send(data)

            response = ws.recv()

            jsonResponse = json.loads(response)

            des = DES.new(private_key, DES.MODE_ECB)
            encrypted_text = jsonResponse['Response']['report']['encrypted_text']
            b = base64.b64decode(encrypted_text)
            data = des.decrypt(b).decode()

            if not flag in data:
                'Not report'
                close(CORRUPT)

            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

    elif vuln == 4:
        arg = sys.argv[3].split(':')

        username = arg[0]
        password = arg[1]

        flag = sys.argv[4]

        s = requests.Session()

        try:
            response = s.post('http://{}:{}/api/login'.format(ip, port),
                              json={'username': username, 'password': password},
                              timeout=(CT, RT)).text
            if not 'User' in response:
                print("Can't login")
                close(CORRUPT)
        except Exception as e:
            print(str(e))
            close(MUMBLE)

        try:
            response = s.get('http://{}:{}/api/get_transactions'.format(ip, port), timeout=(CT, RT)).text

            if not flag in response:
                print('Not transaction msg')
                close(CORRUPT)
            close(OK)
        except Exception as e:
            print(str(e))
            close(MUMBLE)


if __name__ == "__main__":
    if cmd == 'check':
        check()
    elif cmd == 'get':
        get()
    elif cmd == 'put':
        put()
