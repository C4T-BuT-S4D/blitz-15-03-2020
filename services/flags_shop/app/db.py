from datetime import datetime as dt
from app.security import generate_password_hash
import asyncpgsa
import aiomysql
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)
from sqlalchemy.sql import select, and_, or_

import trafaret as t
from trafaret.contrib.object_id import MongoId

sufferers = t.Dict({
    t.Key('_id'): MongoId(),
    t.Key('username'): t.String(max_length=50),
    t.Key('email'): t.Email
})

reports = t.Dict({
    t.Key('_id'): MongoId(),
    t.Key('sufferer_id'): MongoId(),
    t.Key('username'): t.String(max_length=50),
    t.Key('encrypted_text'): t.Bytes(),
    t.Key('private_key'): t.Bytes()

})

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(44), nullable=False, unique=True),
    Column('password_hash', String(128), nullable=False),
    Column('coins', Integer, nullable=False, default=20)
)

flags = Table(
    'flags', metadata,
    Column('id', Integer, primary_key=True),
    Column('seller_id', Integer, ForeignKey('users.id')),
    Column('name', String(64), nullable=False, unique=True),
    Column('description', String(64), nullable=False),
    Column('cost', Integer, nullable=False),
    Column('in_stock', Integer, nullable=False)
)

orders = Table(
    'orders', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('flags_id', Integer, ForeignKey('flags.id')),
    Column('name', String(64), nullable=False),
    Column('description', String(64), nullable=False),
    Column('created_date', DateTime, default=dt.now())
)

transactions = Table(
    'transactions', metadata,
    Column('id', Integer, primary_key=True),
    Column('from_user_id', Integer, ForeignKey('users.id')),
    Column('to_user_id', Integer, ForeignKey('users.id')),
    Column('msg', String(64)),
    Column('value', Integer, nullable=False),
    Column('created_date', DateTime, default=dt.now())
)


async def init_db(app):
    dsn = construct_db_url(app['config']['database'])
    pool = await asyncpgsa.create_pool(dsn=dsn)
    app['db_pool'] = pool
    return pool


def construct_db_url(config):
    DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"
    return DSN.format(
        user=config['DB_USER'],
        password=config['DB_PASS'],
        database=config['DB_NAME'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
    )


async def get_user_by_name(conn, username):
    result = await conn.fetchrow(
        users
            .select()
            .where(users.c.username == username)
    )
    return result


async def get_flag_by_name(conn, name):
    result = await conn.fetchrow(
        flags
            .select()
            .where(flags.c.name == name)
    )
    return result


async def have_flag(conn, user_id, name):
    result = await conn.fetchrow(
        orders
            .select()
            .where(and_(orders.c.user_id == user_id, orders.c.name == name))
    )
    return result


async def buy_flag(conn, user_id, name, cost, flags_id, description):
    result = await conn.execute(users.
                                update(users).
                                values(coins=(users.c.coins - cost)).
                                where(users.c.id == user_id))

    result = await conn.execute(orders
        .insert()
        .values(
        {'user_id': user_id,
         'flags_id': flags_id,
         'name': name,
         'description': description,
         'created_date': dt.now()
         }))

    result = await conn.execute(flags.
                                update(flags).
                                values(in_stock=(flags.c.in_stock - 1)).
                                where(flags.c.name == name))

    return result


async def insert_user(conn, username, password):
    result = await conn.execute(users
        .insert()
        .values(
        {'username': username,
         'password_hash': generate_password_hash(password)}))
    return result


async def add_flag(conn, user_id, name, description, cost, in_stock):
    result = await conn.execute(flags
        .insert()
        .values(
        {'seller_id': user_id,
         'name': name,
         'description': description,
         'cost': cost,
         'in_stock': in_stock}))
    return result


async def delete_order(conn, user_id, name):
    result = await conn.execute(orders.
                                delete().
                                where(and_(orders.c.name == name, orders.c.user_id == user_id)))
    return result


async def send_money(conn, user_id, receiver, value, msg):
    user_receiver = await get_user_by_name(conn, receiver)
    result = await conn.execute(transactions
        .insert()
        .values(
        {'from_user_id': user_id,
         'to_user_id': user_receiver['id'],
         'msg': msg,
         'value': value,
         'created_date': dt.now()
         }))

    result = await conn.execute(users.
                                update(users).
                                values(coins=(users.c.coins - value)).
                                where(users.c.id == user_id))

    result = await conn.execute(users.
                                update(users).
                                values(coins=(users.c.coins + value)).
                                where(users.c.username == receiver))
    return result


async def get_users(conn):
    select_stmt = select([users.c.username])
    result = await conn.fetch(select_stmt)
    users_list = []
    for row in result:
        users_list.append(row['username'])
    return users_list


async def get_flags(conn):
    select_stmt = select([flags.c.name, flags.c.cost, flags.c.in_stock])
    result = await conn.fetch(select_stmt)
    flags_list = []
    for row in result:
        flags_list.append({'name': row['name'], 'cost': row['cost'], 'in_stock': row['in_stock']})
    return flags_list


async def get_orders(conn, user_id):
    select_stmt = select([orders.c.name, orders.c.description]).where(orders.c.user_id == user_id)
    result = await conn.fetch(select_stmt)
    orders_list = []
    for row in result:
        orders_list.append({'name': row['name'], 'description': row['description']})
    return orders_list


async def get_transactions(conn, user_id):
    select_stmt = select([transactions.c.from_user_id, transactions.c.to_user_id,
                          transactions.c.msg, transactions.c.value]).where \
        (or_(transactions.c.from_user_id == user_id, transactions.c.to_user_id == user_id))
    result = await conn.fetch(select_stmt)
    transactions_list = []
    for row in result:
        transactions_list.append({'from_user_id': row['from_user_id'],
                                  'to_user_id': row['to_user_id'], 'msg': row['msg'], 'value': row['value']})
    return transactions_list


async def get_products(conn, user_id):
    select_stmt = select([flags.c.name, flags.c.cost, flags.c.in_stock]).where(flags.c.seller_id == user_id)
    result = await conn.fetch(select_stmt)
    products_list = []
    for row in result:
        products_list.append({'name': row['name'], 'cost': row['cost'], 'in_stock': row['in_stock']})
    return products_list
