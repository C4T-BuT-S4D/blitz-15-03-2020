#!/usr/bin/env python3

from gevent import monkey

monkey.patch_all()

import os
import random
import sys
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shop_lib import *


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)
        self.ws = None

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')
        except websocket._exceptions.WebSocketTimeoutException:
            self.cquit(Status.DOWN, 'Websocket timeout', 'Got WebSocketTimeoutException')
        finally:
            if self.ws:
                self.ws.close()

    def check(self):
        self.mch.get_ws_conn()
        self.cquit(Status.OK)

    def put(self, flag_id, flag, vuln):
        vuln = int(vuln)
        if vuln == 4:
            username, password = self.mch.register()
            s = self.mch.login(username, password)
            # add real flag
            self.mch.add_item(
                sess=s,
                name=rnd_string(20),
                description=flag,
                cost=((1 << 31) - 1),
                in_stock=random.randint(1000, 2000),
            )

            # add fake item
            fake_name = rnd_string(random.randint(20, 30))
            fake_description = rnd_string(random.randint(40, 60))
            self.mch.add_item(
                sess=s,
                name=fake_name,
                description=fake_description,
                cost=random.randint(1, 100),
                in_stock=random.randint(1000, 20000),
            )

            self.cquit(Status.OK, f'{fake_name}:{fake_description}')

        elif vuln == 1:
            username = rnd_username()
            ws = self.mch.get_ws_conn()
            ws.recv()
            self.mch.send_comment(username=username, comment=flag, private='TRUE')

            self.cquit(Status.OK, f'{username}')

        elif vuln == 2:
            username = rnd_username()
            email = rnd_string(20)
            ws = self.mch.get_ws_conn()
            ws.recv()
            data = self.mch.create_report(username=username, email=email, text=flag)
            self.assert_in('Response', data, 'Invalid data from report creation')
            self.assert_in('object_id', data['Response'], 'Invalid data from report creation')
            self.assert_in('private_key', data['Response'], 'Invalid data from report creation')
            object_id = data['Response']['object_id']
            private_key = data['Response']['private_key']

            self.cquit(Status.OK, f'{object_id}:{private_key}')

        elif vuln == 3:
            sender, sender_pass = self.mch.register()
            receiver, receiver_pass = self.mch.register()
            sender_sess = self.mch.login(sender, sender_pass)
            self.mch.send_message(sess=sender_sess, receiver=receiver, value=1, msg=flag)

            self.cquit(Status.OK, f'{receiver}:{receiver_pass}')

        self.cquit(Status.ERROR, f'PUT error', f'Invalid vuln number')

    def get(self, flag_id, flag, vuln):
        vuln = int(vuln)

        if vuln == 4:
            username, password = self.mch.register()
            sess = self.mch.login(username, password)

            # TODO: remove this vuln?
            self.cquit(Status.OK)
        elif vuln == 1:
            ws = self.mch.get_ws_conn()
            ws.recv()
            data = self.mch.get_my_comments(username=flag_id)
            self.assert_in(flag, data, 'Invalid comments', status=Status.CORRUPT)

            self.cquit(Status.OK)

        elif vuln == 2:
            object_id, private_key = flag_id.split(':')
            ws = self.mch.get_ws_conn()
            ws.recv()
            data = self.mch.get_report(object_id=object_id, private_key=private_key, stat=Status.CORRUPT)
            self.assert_in(flag, data, 'No flag in report', status=Status.CORRUPT)
            self.cquit(Status.OK)

        elif vuln == 3:
            username, password = flag_id.split(':')
            sess = self.mch.login(username, password, stat=Status.CORRUPT)
            data = self.mch.get_transactions(sess, stat=Status.CORRUPT)
            self.assert_in(flag, data, 'No flag in transactions', status=Status.CORRUPT)
            self.cquit(Status.OK)

        self.cquit(Status.ERROR, f'GET error', f'Invalid vuln number')


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
