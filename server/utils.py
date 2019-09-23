from sqlalchemy.sql import text
from asyncpg.pool import PoolConnectionProxy
from uuid import uuid4, UUID


async def get_unique_uuid(conn: PoolConnectionProxy) -> UUID:
    while True:
        uuid = uuid4()
        query = text(f'SELECT name FROM accounts WHERE uuid=\'{uuid}\';')
        result = await conn.fetch(query)
        if len(result) == 0:
            return uuid

async def check_uuid(conn: PoolConnectionProxy, uuid) -> bool:
    query = text(f'SELECT name FROM accounts WHERE uuid=\'{uuid}\';')
    result = await conn.fetch(query)
    if len(result) == 0:
        return False
    return True
