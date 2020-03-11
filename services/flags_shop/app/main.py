import asyncio

import aiohttp_jinja2
import aiomysql
import aioredis
import jinja2
import motor.motor_asyncio as aiomotor
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import authorized_userid
from aiohttp_security import setup as setup_security
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage

from app.db import init_db
from app.db_auth import DBAuthorizationPolicy
from app.routes import setup_routes
from app.settings import load_config, PACKAGE_NAME
from app.ws import WsHandler


async def init_mongo(app, loop):
    mongo_uri = "mongodb://{}:{}".format(app['config']['database']['MONGO_HOST'],
                                         app['config']['database']['MONGO_PORT'])
    conn = aiomotor.AsyncIOMotorClient(
        mongo_uri,
        maxPoolSize=app['config']['database']['MAX_POOL_SIZE'],
        io_loop=loop)
    db_name = app['config']['database']['MONGO_DB_NAME']

    return conn[db_name]


async def setup_mongo(app, loop):
    mongo = await init_mongo(app, loop)

    async def close_mongo(app):
        mongo.client.close()

    app.on_cleanup.append(close_mongo)
    return mongo


async def setup_redis(app):
    pool = await aioredis.create_redis_pool((
        app['config']['database']['REDIS_HOST'],
        app['config']['database']['REDIS_PORT']
    ))

    async def close_redis(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_redis)
    app['redis_pool'] = pool

    return pool


async def setup_mysql(app, loop):
    pool = await aiomysql.create_pool(host=app['config']['database']['MYSQL_HOST'],
                                      port=app['config']['database']['MYSQL_PORT'],
                                      user=app['config']['database']['MYSQL_USER'],
                                      password=app['config']['database']['MYSQL_PASSWORD'],
                                      db=app['config']['database']['MYSQL_DB_NAME'], loop=loop, autocommit=True)

    async def close_mysql(app):
        pool.close()
        await pool.wait_closed()

    app.on_cleanup.append(close_mysql)
    app['mysql_pool'] = pool

    return pool


async def current_user_ctx_processor(request):
    username = await authorized_userid(request)
    is_anonymous = not bool(username)
    return {'current_user': {'is_anonymous': is_anonymous}}


async def shutdown(app):
    for ws in app['websockets'].values():
        await ws.close()
    app['websockets'].clear()


async def init_app(config, loop):
    app = web.Application()

    app['config'] = config

    app['websockets'] = {}

    app.on_shutdown.append(shutdown)

    db_pool = await init_db(app)

    mysql_pool = await setup_mysql(app, loop)

    mongo_pool = await setup_mongo(app, loop)

    redis_pool = await setup_redis(app)

    ws_handler = WsHandler(redis_pool, mongo_pool, mysql_pool)

    setup_routes(app, ws_handler)

    setup_session(app, RedisStorage(redis_pool))

    # needs to be after session setup because of `current_user_ctx_processor`
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader(PACKAGE_NAME),
        context_processors=[current_user_ctx_processor],
    )

    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(db_pool)
    )

    return app


async def get_app(configpath):
    config = load_config(configpath)
    # logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    app = await init_app(config, loop)
    return app


async def app_wrapper():
    return await get_app('../config/user.toml')


if __name__ == '__main__':
    web.run_app(app_wrapper())
