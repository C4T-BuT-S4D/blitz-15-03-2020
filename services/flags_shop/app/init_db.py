from sqlalchemy import create_engine, MetaData
from datetime import datetime

from app.db import construct_db_url
from app.db import users, flags, orders, transactions
from app.security import generate_password_hash
from app.settings import load_config

from Crypto.Cipher import DES
from time import sleep

import motor.motor_asyncio as aiomotor
import asyncio
from faker import Factory
from bson import ObjectId
from app.db import sufferers, reports
import random, string

import aiomysql


async def init_mongo(config, loop):
    mongo_uri = "mongodb://{}:{}".format(config['MONGO_HOST'], config['MONGO_PORT'])
    conn = aiomotor.AsyncIOMotorClient(
        mongo_uri,
        maxPoolSize=config['MAX_POOL_SIZE'],
        io_loop=loop)
    db_name = config['MONGO_DB_NAME']
    return conn[db_name]


def setup_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']
    db_pass = target_config['DB_PASS']

    with engine.connect() as conn:
        teardown_db(executor_config=executor_config,
                    target_config=target_config)

        conn.execute("CREATE USER %s WITH PASSWORD '%s'" % (db_user, db_pass))
        conn.execute("CREATE DATABASE %s" % db_name)
        conn.execute("GRANT ALL PRIVILEGES ON DATABASE %s TO %s" %
                     (db_name, db_user))


def teardown_db(executor_config=None, target_config=None):
    engine = get_engine(executor_config)

    db_name = target_config['DB_NAME']
    db_user = target_config['DB_USER']

    with engine.connect() as conn:
        # terminate all connections to be able to drop database
        conn.execute("""
          SELECT pg_terminate_backend(pg_stat_activity.pid)
          FROM pg_stat_activity
          WHERE pg_stat_activity.datname = '%s'
            AND pid <> pg_backend_pid();""" % db_name)
        conn.execute("DROP DATABASE IF EXISTS %s" % db_name)
        conn.execute("DROP ROLE IF EXISTS %s" % db_user)


def get_engine(db_config):
    db_url = construct_db_url(db_config)
    engine = create_engine(db_url, isolation_level='AUTOCOMMIT')
    return engine


def create_tables(target_config=None):
    engine = get_engine(target_config)
    meta = MetaData()
    meta.create_all(bind=engine, tables=[users, flags, orders, transactions])


def drop_tables(target_config=None):
    engine = get_engine(target_config)

    meta = MetaData()
    meta.drop_all(bind=engine, tables=[users, flags, orders, transactions])


def create_sample_data(target_config=None):
    engine = get_engine(target_config)

    with engine.connect() as conn:
        conn.execute(users.insert(), [
            {'id': 2000000001,
             'username': 'admin',
             'password_hash': generate_password_hash('admin')},
            {'id': 2000000002,
             'username': 'root',
             'password_hash': generate_password_hash('root')},
        ])
        conn.execute(flags.insert(), [
            {'id': 2000000001, 'seller_id': 2000000001, 'name': '317c6e65-7e38-481a-9227-edbdae51836c',
             'description': '0N3KYAYIAR43482F6EQN60ZH8AIHWVJM=', 'cost': 1, 'in_stock': 2},
            {'id': 2000000002, 'seller_id': 2000000001, 'name': '88ec2d5a-2330-4181-819a-db2c4d6dd628',
             'description': '423A4JFGKG5MCUCZZUGYE6IQ220IY0UG=', 'cost': 1, 'in_stock': 1},
            {'id': 2000000003, 'seller_id': 2000000002, 'name': '22aba0f9-ccaf-404d-b6c2-5b5dda1e5a63',
             'description': '8WJTQ6UQX5ZQV7DOINDM3Y9BX6D8IEJR=', 'cost': 2, 'in_stock': 6},
        ])
        conn.execute(orders.insert(), [
            {'id': 2000000001, 'user_id': 2000000001, 'flags_id': 2000000001,
             'name': '317c6e65-7e38-481a-9227-edbdae51836c',
             'description': '0N3KYAYIAR43482F6EQN60ZH8AIHWVJM=', 'created_date': datetime.now()},
            {'id': 2000000002, 'user_id': 2000000001, 'flags_id': 2000000002,
             'name': '88ec2d5a-2330-4181-819a-db2c4d6dd628',
             'description': '423A4JFGKG5MCUCZZUGYE6IQ220IY0UG=', 'created_date': datetime.now()}
        ])
        conn.execute(transactions.insert(), [
            {'id': 2000000001, 'from_user_id': 2000000001, 'to_user_id': 2000000002,
             'msg': 'ENRVLN3SYOJDRY1JM025RM7P96OSZ08O=',
             'value': 2, 'created_date': datetime.now()},
            {'id': 2000000002, 'from_user_id': 2000000002, 'to_user_id': 2000000001,
             'msg': '333ZG3JX4BPAWC6JLQHILMLAVY2ABQU4=',
             'value': 4, 'created_date': datetime.now()},
        ])


async def prepare_coolections(*collections):
    for coll in collections:
        await coll.drop()


async def insert_data(collection, values):
    await collection.insert_many(values)
    return values


async def generate_sufferers(mongo, schema, rows, fake):
    values = []
    for i in range(rows):
        values.append(schema({
            '_id': ObjectId(),
            'username': fake.user_name()[:50],
            'email': fake.email(),
        }))
    users = await insert_data(mongo, values)
    return users


def generator(size=31, chars=string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size)) + '='


def pad(text):
    while len(text) % 8 != 0:
        text += b' '
    return text


async def generate_reports(mongo, schema, rows, fake, users):
    values = []
    for user in users:
        for i in range(rows):
            key = ''.join(random.choice(string.digits) for _ in range(8))
            des = DES.new(key, DES.MODE_ECB)
            text = generator()
            padded_text = pad(text)
            encrypted_text = des.encrypt(padded_text)
            values.append(schema({
                '_id': ObjectId(),
                'sufferer_id': ObjectId(user['_id']),
                'username': user['username'],
                'encrypted_text': encrypted_text,
                'private_key': key.encode(),
            }))

    ids = await insert_data(mongo, values)
    return ids


async def init(loop, config):
    mongo = await init_mongo(config, loop)
    fake = Factory.create()
    fake.seed(1234)
    await prepare_coolections(mongo.sufferers, mongo.reports)

    users = await generate_sufferers(mongo.sufferers, sufferers, 4, fake)
    await generate_reports(mongo.reports, reports, 1, fake, users)


async def generate_mysql(loop, executor_config):
    admin_conn = await aiomysql.connect(host=executor_config['MYSQL_HOST'], port=executor_config['MYSQL_PORT'],
                                        user=executor_config['MYSQL_USER'], password=executor_config['MYSQL_PASSWORD'],
                                        db=executor_config['MYSQL_DB_NAME'],
                                        loop=loop)
    cur = await admin_conn.cursor()
    async with admin_conn.cursor() as cur:
        try:
            await cur.execute("insert into users (username) values ('root')")
        except:
            pass
        try:
            await cur.execute("insert into users (username) values ('admin')")
        except:
            pass
        try:
            await cur.execute(
                "insert into comments (text, private, author_id) values ('DBH5DM1QTAFNUW3JWPYTO6UZ83X0ZD1Z=', TRUE, (select user_id from users where username='root'))")
        except:
            pass
        try:
            await cur.execute(
                "insert into comments (text, private, author_id) values ('75MPGF37DPBLK22F358W3547FUI0R0DK=', FALSE, (select user_id from users where username='admin'))")
        except:
            pass
        await admin_conn.commit()
    admin_conn.close()


async def init_mysql(loop, executor_config):
    admin_conn = await aiomysql.connect(host=executor_config['MYSQL_HOST'], port=executor_config['MYSQL_PORT'],
                                        user=executor_config['MYSQL_USER'],
                                        password=executor_config['MYSQL_PASSWORD'],
                                        db=executor_config['MYSQL_DB_NAME'],
                                        loop=loop)
    cur = await admin_conn.cursor()
    async with admin_conn.cursor() as cur:
        try:
            await cur.execute(
                "create table flags_shop.users (user_id INT primary key AUTO_INCREMENT, username VARCHAR(44) NOT NULL UNIQUE)")
        except Exception as ex:
            pass
        try:
            await cur.execute(
                "create table flags_shop.comments (comment_id INT primary key AUTO_INCREMENT, text VARCHAR(64) NOT NULL, private BOOLEAN NOT NULL, author_id INT)")
        except Exception as ex:
            pass
        try:
            await cur.execute(
                "alter table flags_shop.comments ADD FOREIGN KEY (author_id) REFERENCES users(user_id)")
        except Exception as ex:
            pass
        await admin_conn.commit()
    admin_conn.close()


if __name__ == "__main__":
    admin_db_config = load_config('config/admin.toml')['database']
    user_db_config = load_config('config/user.toml')['database']
    teardown_db(executor_config=admin_db_config, target_config=user_db_config)
    setup_db(executor_config=admin_db_config, target_config=user_db_config)
    create_tables(target_config=user_db_config)
    create_sample_data(target_config=user_db_config)
    mongo_loop = asyncio.get_event_loop()
    mysql_loop = asyncio.get_event_loop()
    mongo_loop.run_until_complete(init(mongo_loop, user_db_config))
    mysql_loop.run_until_complete(init_mysql(mysql_loop, admin_db_config))
    mysql_loop.run_until_complete(generate_mysql(mysql_loop, admin_db_config))
