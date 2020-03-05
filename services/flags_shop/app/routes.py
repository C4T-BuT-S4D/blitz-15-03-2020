from aiohttp import web
from app.views import login, register, logout, \
    get_users, get_orders, get_flags, \
    get_transactions, get_my_flags, add, delete_order, \
    send, buy, get_user, index


def setup_routes(app, handler):
    app.router.add_get('/api/', index, name='index')
    app.router.add_post('/api/login', login, name='login')
    app.router.add_post('/api/register', register, name='register')
    app.router.add_get('/api/get_user', get_user, name='get_user')

    app.router.add_get('/api/logout', logout, name='logout')

    app.router.add_get('/api/get_users', get_users, name='get_users')

    app.router.add_get('/api/get_flags', get_flags, name='get_flags')
    app.router.add_post('/api/buy', buy, name='buy')

    app.router.add_get('/api/get_orders', get_orders, name='get_orders')
    app.router.add_post('/api/delete_order', delete_order, name='delete_order')

    app.router.add_post('/api/add', add, name='add')
    app.router.add_get('/api/get_my_flags', get_my_flags, name='get_my_flags')

    app.router.add_post('/api/send', send, name='send')
    app.router.add_get('/api/get_transactions', get_transactions, name='get_transactions')

    app.router.add_get('/api/ws', handler.ws, name='ws')
