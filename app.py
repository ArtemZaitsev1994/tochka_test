from aiohttp import web
import json
from aiopg.sa import create_engine
from sqlalchemy.sql import text
from routes import routes
import asyncpgsa


async def create_aiopg(app):
    app['db'] = await asyncpgsa.create_pool(
        user='tochka',
        database='tochka_db',
        host='localhost',
        port=5432,
        password='strongPASS'
    )


async def check_tables(app):
    async with app['db'].acquire() as conn:
        query = text("""
            CREATE TABLE IF NOT EXISTS accounts 
            (
                uuid UUID PRIMARY KEY,
                name VARCHAR(32),
                balance INTEGER DEFAULT 0,
                hold INTEGER,
                status BOOLEAN

            );
        """)
        r = await conn.fetch(query)


async def close_aiopg(app):
    app['db'].close()
    await app['db'].wait_closed()

app = web.Application()

app.on_startup.append(create_aiopg)
app.on_startup.append(check_tables)
app.on_cleanup.append(close_aiopg)

for route in routes:
    app.router.add_route(route[0], route[1], route[2], name=route[3])

if __name__ == '__main__':
    web.run_app(app)
