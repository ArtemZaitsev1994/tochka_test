import json
import asyncpgsa
import pytest

from aiohttp import web
from sqlalchemy.sql import text
from routes import routes


TEST_DATA = [
    ['26c940a1-7228-4ea2-a3bc-e6460b172040', 'Петров Иван Сергеевич', 1700, 300, 'открыт'],
    ['7badc8f8-65bc-449a-8cde-855234ac63e1', 'Kazitsky Jason', 200, 200, 'открыт'],
    ['5597cc3d-c948-48a0-b711-393edf20d9c0', 'Пархоменко Антон Александрович', 10, 300, 'открыт'],
    ['867f0924-a917-4711-939b-90b179a96392', 'Петечкин Петр Измаилович', 1000000, 1, 'закрыт']
]

async def create_aiopg(app):
    app['db'] = await asyncpgsa.create_pool(
        user='tochka',
        database='test',
        host='localhost',
        port=5432,
        password='strongPASS'
    )


async def check_tables(app):
    async with app['db'].acquire() as conn:
        query_drop_table = text('DROP TABLE accounts;')
        await conn.fetch(query_drop_table)
        query = text("""
        CREATE TABLE accounts 
            (
                uuid UUID PRIMARY KEY,
                name VARCHAR(32),
                balance INTEGER DEFAULT 0,
                hold INTEGER,
                status BOOLEAN

            );""")
        r = await conn.fetch(query)

async def create_accounts(app):
    async with app['db'].acquire() as conn:
        for acc in TEST_DATA:
            uuid, name, balance, hold, status = acc
            status = (status == 'открыт')
            query = text(f"""
                INSERT INTO accounts VALUES(
                \'{uuid}\',
                \'{name}\',
                {balance},
                {hold},
                {status});""")
            await conn.fetch(query)

async def close_aiopg(app):
    await app['db'].close()


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()

    app.on_startup.append(create_aiopg)
    app.on_startup.append(check_tables)
    app.on_startup.append(create_accounts)
    app.on_cleanup.append(close_aiopg)
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])
    return loop.run_until_complete(aiohttp_client(app))


async def test_ping_server(cli):
    # пингуем сервер
    resp = await cli.get('/api/ping')
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert "pong" == answer['description']['message']


async def test_get_all_accounts(cli):
    # получаем все акккаунты из базы
    resp = await cli.get('/api/accounts')
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['status'] == 200

async def test_get_all_accounts_from_empty_base(cli):
    # проверка на ответ из пустой базы
    async with cli.app['db'].acquire() as conn:
        await conn.fetch(text('TRUNCATE accounts;'))
    resp = await cli.get('/api/accounts')
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert 'No accounts in base.' == answer['description']['message']


async def test_add_money_to_account(cli):
    # тест на увелечение баланса
    # берем идентификатор из тестовых данных
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172040'
    # добавляем денег на счет
    resp = await cli.post('api/add', json={'uuid': uuid, 'balance': 100})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'New balance for account {uuid} is 1800.'

async def test_add_money_to_closed_account(cli):
    # тест на увеличение баланса закрытого аккаунта
    # берем идентификатор закрытого аккаунта из тестовых данных
    uuid = '867f0924-a917-4711-939b-90b179a96392'
    # добавляем денег на счет
    resp = await cli.post('api/add', json={'uuid': uuid, 'balance': 100})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['result'] is False
    assert answer['description']['message'] == 'Account\'s status is "closed".'


async def test_substract_money(cli):
    # тест на снятие денег
    # берем идентификатор из тестовых данных
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172040'
    # вычитаем деньги со счета (hold+substract)
    resp = await cli.post('api/substract', json={'uuid': uuid, 'balance': 100})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'New balance for account {uuid} is 1300.'

async def test_substract_money_more_then_it_have(cli):
    # тест на снятие суммы большой, чем есть на аккаунте
    # берем идентификатор из тестовых данных
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172040'
    # вычитаем деньги со счета (hold+substract)
    resp = await cli.post('api/substract', json={'uuid': uuid, 'balance': 10000})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['result'] is False
    assert answer['description']['message'] == 'Not enough money to substract. Current balance - 1700.'

async def test_substract_money_from_closed_account(cli):
    # тест на снятие денег с закрытого аккаунта
    # берем идентификатор закрытого аккаунта из тестовых данных
    uuid = '867f0924-a917-4711-939b-90b179a96392'
    # вычитаем деньги со счета (hold+substract)
    resp = await cli.post('api/substract', json={'uuid': uuid, 'balance': 100})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == 'Account\'s status is "closed".'


async def test_create_account(cli):
    # тест создания аккаунта
    data = {
        'name': 'Ivan Ivanov',
        'balance': 1000,
        'hold': 0,
        'status': True
    }
    resp = await cli.post('api/status', json=data)
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['status'] == 200

async def test_create_account_with_russian_cyrillic(cli):
    # тест создания аккаунта с русскими буквами
    data = {
        'name': 'Иван Неиванов',
        'balance': 1000,
        'hold': 1,
        'status': True
    }
    resp = await cli.post('api/status', json=data)
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['status'] == 200

async def test_create_account_with_wrong_balance(cli):
    # тест создание аккаунта со строковым балансом
    data = {
        'name': 'Иван Неиванов',
        'balance': 'error',
        'hold': 1,
        'status': True
    }
    resp = await cli.post('api/status', json=data)
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['status'] == 500
    assert answer['description']['message'] == f'Wrong format for "balance" column.'

async def test_create_account_with_wrong_hold(cli):
    # тест создание аккаунта со строковым резервом
    data = {
        'name': 'Иван Неиванов',
        'balance': 100,
        'hold': 'error',
        'status': True
    }
    resp = await cli.post('api/status', json=data)
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['status'] == 500
    assert answer['description']['message'] == f'Wrong format for "hold" column.'


async def test_switch_to_closed_status(cli):
    # тест смены аккаунта в закрытое состояние
    # берем идентификатор из тестовых данных
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172040'
    resp = await cli.delete('api/status', json={'uuid': uuid})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'{uuid} account\'s status now is "closed".'

async def test_switch_to_closed_status_unexisted_account(cli):
    # смена несуществующего аккаунта в закрытое состояние
    # берем идентификатор из тестовых данных
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172048'
    resp = await cli.delete('api/status', json={'uuid': uuid})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'Account {uuid} doesn\'t exist.'

async def test_switch_to_open_status(cli):
    # тест смена статуса аккаунта в открытое состояние
    # берем идентификатор из тестовых данных
    uuid = '867f0924-a917-4711-939b-90b179a96392'
    resp = await cli.put('api/status', json={'uuid': uuid})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'{uuid} account\'s status now is "open".'

async def test_switch_to_open_status_unexisted_account(cli):
    # тест смена статуса несущствующего аккаунта
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b172048'
    resp = await cli.put('api/status', json={'uuid': uuid})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == f'Account {uuid} doesn\'t exist.'


async def test_get_not_existed_account_by_uuid(cli):
    # тест получения данных о несуществующем аккаунте
    # взяли несуществующий аккаунт
    uuid = '26c940a1-7228-4ea2-a3bc-e6460b102040'
    resp = await cli.get('api/status', json={'uuid': uuid, 'name': None})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    assert answer['description']['message'] == 'No matches in base.'

async def test_get_account_by_uuid(cli):
    # тест получения аккаунта по uuid
    # взяли несуществующий аккаунт
    uuid = '867f0924-a917-4711-939b-90b179a96392'
    resp = await cli.get('api/status', json={'uuid': uuid, 'name': None})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    result = (
        'Found accounts:\n'
        'UUID - 867f0924-a917-4711-939b-90b179a96392 | '
        'name - Петечкин Петр Измаилович | '
        'balance - 1000000 | '
        'hold - 1 | status - closed.\n'
    )
    assert answer['description']['message'] == result

async def test_get_accounts_by_name(cli):
    # тест получения аккаунтов по имени
    # взяли несуществующий аккаунт
    name = 'тр'
    resp = await cli.get('api/status', json={'uuid': None, 'name': name})
    assert resp.status == 200
    answer = json.loads(await resp.text())
    result = (
        'Found accounts:\n'
        'UUID - 26c940a1-7228-4ea2-a3bc-e6460b172040 | '
        'name - Петров Иван Сергеевич | '
        'balance - 1700 | '
        'hold - 300 | status - open.\n'
        'UUID - 867f0924-a917-4711-939b-90b179a96392 | '
        'name - Петечкин Петр Измаилович | '
        'balance - 1000000 | '
        'hold - 1 | status - closed.\n'
    )
    assert answer['description']['message'] == result
