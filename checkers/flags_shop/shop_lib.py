import base64
import json

import websocket
from Crypto.Cipher import DES
from checklib import *

PORT = 9090


class CheckMachine:
    def __init__(self, checker: BaseChecker):
        self.c = checker

    @property
    def url(self):
        return f'http://{self.c.host}:{PORT}'

    def get_ws_conn(self):
        if self.c.ws is None:
            self.c.ws = websocket.create_connection(f'ws://{self.c.host}:{PORT}/api/ws', timeout=5)
        return self.c.ws

    def register(self, username=None, password=None):
        username = username or rnd_username()
        password = password or rnd_password()

        sess = get_initialized_session()
        r = sess.post(f'{self.url}/api/register', json={'username': username, 'password': password})
        self.c.check_response(r, 'Could not register')
        data = self.c.get_text(r, 'Could not register')
        self.c.assert_in('Ok', data, 'Could not register')

        return username, password

    def login(self, username, password, stat=Status.MUMBLE):
        sess = get_initialized_session()
        r = sess.post(f'{self.url}/api/login', json={'username': username, 'password': password})
        self.c.check_response(r, 'Could not login')
        data = self.c.get_text(r, 'Could not login')
        self.c.assert_in('User', data, 'Invalid page after login', status=stat)
        return sess

    def add_item(self, sess, name, description, cost, in_stock):
        r = sess.post(
            f'{self.url}/api/add',
            json={
                'name': name,
                'description': description,
                'cost': cost, 'in_stock': in_stock,
            },
        )
        self.c.check_response(r, 'Could not add item')
        data = self.c.get_text(r, 'Could not add item')
        self.c.assert_in('Ok', data, 'Could not add item')

    def send_comment(self, username, comment, private):
        data = json.dumps({
            'action': 'send_comment',
            'data': {
                'username': username,
                'comment': comment,
                'private': private,
            },
        })
        self.c.ws.send(data)
        resp = self.c.ws.recv()
        self.c.assert_in('ok', resp, 'Could not send comment')
        return resp

    def create_report(self, username, email, text):
        data = json.dumps({
            'action': 'create_report',
            'data': {
                'username': username,
                'email': email,
                'text': text,
            },
        })
        self.c.ws.send(data)
        resp = self.c.ws.recv()
        self.c.assert_in('ok', resp, 'Could not create report')
        try:
            data = json.loads(resp)
        except json.JSONDecodeError:
            self.c.cquit(Status.MUMBLE, 'Invalid json from report creation', f'Got response: {resp}')

        return data

    def send_message(self, sess, receiver, value, msg):
        r = sess.post(
            f'{self.url}/api/send',
            json={
                'receiver': receiver,
                'value': value,
                'msg': msg,
            }
        )
        self.c.check_response(r, 'Could not send message')
        data = self.c.get_text(r, 'Could not send message')
        self.c.assert_in('Ok', data, 'Could not send message')
        return data

    def buy_item(self, name):
        pass

    def get_my_comments(self, username):
        data = json.dumps({'action': 'get_my_comments', 'data': username})
        self.c.ws.send(data)
        resp = self.c.ws.recv()
        return resp

    def get_report(self, object_id, private_key, stat=Status.MUMBLE):
        data = json.dumps({'action': 'get_report', 'data': object_id})
        self.c.ws.send(data)
        resp = self.c.ws.recv()
        try:
            data = json.loads(resp)
        except json.JSONDecodeError:
            self.c.cquit(Status.MUMBLE, 'Invalid json response to get_report', f'Got response {resp}')

        self.c.assert_in('Response', data, 'Invalid response to get_report', status=stat)
        self.c.assert_in('report', data['Response'], 'Invalid response to get_report', status=stat)
        self.c.assert_in('encrypted_text', data['Response']['report'], 'Invalid response to get_report', status=stat)
        text = data['Response']['report']['encrypted_text']
        try:
            enc_text = base64.b64decode(text)

            des = DES.new(private_key.encode(), DES.MODE_ECB)
            data = des.decrypt(enc_text).decode()

            return data
        except Exception as e:
            self.c.cquit(stat, 'Invalid encrypted text in report', f'Got decode exception {e}')

    def get_transactions(self, sess, stat=Status.MUMBLE):
        r = sess.get(f'{self.url}/api/get_transactions')
        self.c.check_response(r, 'Could not get transactions')
        data = self.c.get_text(r, 'Could not get transactions', status=stat)
        return data
