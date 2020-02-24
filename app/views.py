from aiohttp import web
from aiohttp_security import remember, forget, authorized_userid

from app import db
from app.forms import validate_login_data,\
    validate_register_data, validate_add_data,\
    validate_delete_data, validate_send_data,\
    validate_buy_data



def redirect(router, route_name):
    location = router[route_name].url_for()
    return web.HTTPFound(location)

async def logout(request):
    response = redirect(request.app.router, 'index')
    await forget(request, response)
    return response

async def register(request):
    try:
        data = await request.json()
    except:
        return web.json_response({'Error': 'Json is required'}, content_type='application/json')

    async with request.app['db_pool'].acquire() as conn:
        error = await validate_register_data(conn, data)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            return web.json_response({'Ok': 'Register success!'}, content_type='application/json')
    return {}

async def login(request):
    try:
        data = await request.json()
    except:
        return web.json_response({'Error': 'Json is required'}, content_type='application/json')

    async with request.app['db_pool'].acquire() as conn:
        error = await validate_login_data(conn, data)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            response = redirect(request.app.router, 'get_user')
            user = await db.get_user_by_name(conn, data['username'])
            await remember(request, response, user['username'])
            raise response
    return {}

async def index(request):
    return web.json_response({'Service': 'Flags.Shop'}, content_type='application/json')


async def buy(request):
    username = await authorized_userid(request)
    if not username:
        return web.json_response({'Error': "You are not authorized"}, content_type='application/json')
    async with request.app['db_pool'].acquire() as conn:
        data = await request.text()
        current_user = await db.get_user_by_name(conn, username)
        error = await validate_buy_data(conn, current_user['id'], current_user['coins'], data)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            return web.json_response({'Ok': "Flag bought!"}, content_type='application/json')

async def send(request):
    username = await authorized_userid(request)
    if not username:
        return web.json_response({'Error': "You are not authorized"}, content_type='application/json')
    async with request.app['db_pool'].acquire() as conn:
        data = await request.text()
        current_user = await db.get_user_by_name(conn, username)
        error = await validate_send_data(conn, current_user['id'], current_user['coins'], data)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            return web.json_response({'Ok': "Money sended"}, content_type='application/json')

async def add(request):
    username = await authorized_userid(request)
    if not username:
        return web.json_response({'Error': "You are not authorized"}, content_type='application/json')
    async with request.app['db_pool'].acquire() as conn:
        data = await request.text()
        current_user = await db.get_user_by_name(conn, username)
        error = await validate_add_data(conn, current_user['id'], data)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            return web.json_response({'Ok': "Item added"}, content_type='application/json')

async def delete_order(request):
    username = await authorized_userid(request)
    if not username:
        return web.json_response({'Error': "You are not authorized"}, content_type='application/json')
    async with request.app['db_pool'].acquire() as conn:
        req = await request.text()
        current_user = await db.get_user_by_name(conn, username)
        error = await validate_delete_data(conn, current_user['id'], req)
        if error:
            return web.json_response({'Error': error}, content_type='application/json')
        else:
            return web.json_response({'Ok': "Item deleted"}, content_type='application/json')

async def get_user(request):
    username = await authorized_userid(request)
    if not username:
        return web.json_response({'Error': "You are not authorized"}, content_type='application/json')
    async with request.app['db_pool'].acquire() as conn:
        data = await db.get_user_by_name(conn, username)
    return web.json_response({'User' : {'username' : username, 'coins' : data['coins']}}, content_type='application/json')

async def get_users(request):
    async with request.app['db_pool'].acquire() as conn:
        users = await db.get_users(conn)
    return web.json_response({'users' : users}, content_type='application/json')

async def get_flags(request):
    async with request.app['db_pool'].acquire() as conn:
        flags = await db.get_flags(conn)
    return web.json_response({'flags' : flags}, content_type='application/json')

async def get_orders(request):
    username = await authorized_userid(request)
    async with request.app['db_pool'].acquire() as conn:
        current_user = await db.get_user_by_name(conn, username)
        orders = await db.get_orders(conn, current_user['id'])
    return web.json_response({'orders' : orders}, content_type='application/json')

async def get_transactions(request):
    username = await authorized_userid(request)
    async with request.app['db_pool'].acquire() as conn:
        current_user = await db.get_user_by_name(conn, username)
        transactions = await db.get_transactions(conn, current_user['id'])
    return web.json_response({'transactions': transactions}, content_type='application/json')

async def get_my_flags(request):
    username = await authorized_userid(request)
    async with request.app['db_pool'].acquire() as conn:
        current_user = await db.get_user_by_name(conn, username)
        my_flags = await db.get_products(conn, current_user['id'])
    return web.json_response({'my_flags': my_flags}, content_type='application/json')
