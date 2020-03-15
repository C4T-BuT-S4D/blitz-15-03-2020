from app import db
from app.security import check_password_hash
import json


async def validate_login_data(conn, data):
    username = data['username']
    password = data['password']

    if not username:
        return 'username is required'
    if not password:
        return 'password is required'

    user = await db.get_user_by_name(conn, username)

    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    else:
        return None


async def validate_register_data(conn, data):
    username = data['username']
    password = data['password']

    if not username:
        return 'username is required'
    if not password:
        return 'password is required'

    if len(username) > 44 or len(password) > 44:
        return 'A lot of characters'

    try:
        await db.insert_user(conn, username, password)
        return None
    except:
        return 'User already exists!'


async def validate_buy_data(conn, user_id, user_coins, data):
    try:
        json_answer = json.loads(data)
    except:
        return 'Json is required'

    name = json_answer['name']

    if not name:
        return 'Field is required'

    flag = await db.get_flag_by_name(conn, name)

    if not flag:
        return 'Flag not found'

    if flag['in_stock'] <= 0:
        return 'Sorry :( Flag not in stock'

    if user_coins < flag['cost']:
        return 'You dont have enough money'

    have = await db.have_flag(conn, user_id, name)

    if have:
        return 'You already have this flag'

    try:
        await db.buy_flag(conn, user_id, name, flag['cost'], flag['id'], flag['description'])
        return None
    except Exception as ex:
        return str(ex)


async def validate_send_data(conn, user_id, user_coins, data):
    try:
        json_answer = json.loads(data)
    except:
        return 'Json is required'

    receiver = json_answer['receiver']
    value = json_answer['value']
    msg = json_answer['msg']

    if not receiver or not value or not msg:
        return 'Field is required'

    try:
        value = int(json_answer['value'])
    except:
        return 'Value must be integer!'

    if value > user_coins:
        return 'You dont have enough money'

    try:
        await db.send_money(conn, user_id, receiver, value, msg)
        return None
    except:
        return 'User does not exists!'


async def validate_add_data(conn, user_id, data):
    try:
        json_answer = json.loads(data)
    except:
        return 'Json is required'

    seller_id = user_id
    name = json_answer['name']
    description = json_answer['description']
    cost = json_answer['cost']
    in_stock = json_answer['in_stock']

    if not name or not description or not cost or not in_stock:
        return 'Field is required'
    try:
        cost = int(json_answer['cost'])
        in_stock = int(json_answer['in_stock'])
    except:
        return 'Cost and in_stock must be integers!'

    if cost < 0 or in_stock < 0:
        return 'Cost and in_stock must be >= 0'

    try:
        await db.add_flag(conn, seller_id, name, description, cost, in_stock)
        return None
    except Exception as ex:
        return str(ex)


async def validate_delete_data(conn, user_id, data):
    try:
        json_answer = json.loads(data)
    except:
        return 'Json is required'
    name = json_answer['name']

    if not name:
        return 'Name is required'
    try:
        await db.delete_order(conn, user_id, name)
        return None
    except Exception as ex:
        return str(ex)
