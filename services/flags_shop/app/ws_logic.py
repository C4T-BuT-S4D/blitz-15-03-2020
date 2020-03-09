from bson import ObjectId
from Crypto.Cipher import DES
import random, string, base64, bson, json

ACTIONS = ['get_cookie', 'get_cookies', 'get_comments', 'get_my_comments', 'send_comment', 'get_reports', 'get_report',
           'create_report']


def pad(text):
    while len(text) % 8 != 0:
        text += b' '
    return text


async def validate_action(redis_conn, mongo, mysql_pool, action, data):
    result = 'Empty'

    if action == 'get_cookie':
        result = await redis_conn.execute('GET', data)
        if result:
            result = json.loads(result.decode())
        else:
            result = 'Empty'

    elif action == 'get_cookies':
        cur = b'0'
        cookies = []
        while cur:
            cur, keys = await redis_conn.scan(cur, match=data)
            for key in keys:
                cookies.append(key.decode())
        if cookies:
            result = {'cookies': cookies}
        else:
            result = 'Empty'

    elif action == 'create_report':
        try:
            username = data['username']
            email = data['email']
            text = data['text']
        except:
            return 'username, email, text is required'

        if username == '' or email == '' or text == '':
            return 'some field is empty ;('

        id = ObjectId()

        try:
            await mongo.sufferers.insert_one({
                '_id': id,
                'username': username,
                'email': email})
        except Exception as ex:
            result = str(ex)

        key = ''.join(random.choice(string.digits) for _ in range(6)) + '00'
        des = DES.new(key, DES.MODE_ECB)
        padded_text = pad(str(text).encode())
        encrypted_text = des.encrypt(padded_text)

        report_id = ObjectId()
        try:
            await mongo.reports.insert_one({
                '_id': report_id,
                'sufferer_id': ObjectId(id),
                'username': username,
                'encrypted_text': encrypted_text,
                'private_key': key.encode()})

            result = {'status': 'ok', 'private_key': key, 'object_id': str(report_id),
                      'encrypted_text': base64.encodebytes(encrypted_text).decode().strip('\n')}
        except Exception as ex:
            result = str(ex)

    elif action == 'get_report':
        try:
            id = data
        except:
            return 'data is required'
        try:
            report = await mongo.reports.find_one({'_id': ObjectId(data)})
            encrypted_text = base64.encodebytes(report['encrypted_text']).decode().strip('\n')
            result = {'report': {'username': report['username'], 'encrypted_text': encrypted_text}}
        except Exception as ex:
            result = str(ex)


    elif action == 'get_reports':
        reports = []
        cursor = mongo.reports.find_raw_batches()
        async for batch in cursor:
            for item in bson.decode_all(batch):
                try:
                    encrypted_text = base64.encodebytes(item['encrypted_text']).decode().strip('\n')
                    reports.append({'username': item['username'], 'encrypted_text': encrypted_text})
                except Exception as ex:
                    result = str(ex)
        result = {'reports': reports}


    elif action == 'send_comment':
        try:
            username = data['username']
            comment = data['comment']
            private = data['private']
        except:
            return 'username, comment, private is required'

        if username == '' or comment == '' or private == '':
            return 'some field is empty ;('

        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    try:
                        await cur.execute("insert into users (username) values (%s)", data['username'])
                    except Exception as ex:
                        pass
                    await cur.execute(
                        "insert into comments (private, text, author_id) values ({}, '{}', (select user_id from users where username='{}'))".format(
                            data['private'], data['comment'], data['username']))
                    await conn.commit()

                    result = {'ok': 'comment sended'}
                except Exception as ex:
                    result = str(ex)

    elif action == 'get_comments':
        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'select case private when (username) then username else \'anonymous\' end text, case private when (username) then text else \'private comment\' end text from comments inner join users on author_id=user_id limit 100')
                result = await cur.fetchall()

    elif action == 'get_my_comments':
        async with mysql_pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    'select text from comments where author_id = (select user_id from users where username = %s)', data)
                result = await cur.fetchall()

    return result
