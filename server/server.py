import json
from aiohttp import web
from sqlalchemy.sql import text
from utils import get_unique_uuid, check_uuid


# стандартный ответ
ANSWER = {
        'status': 200,
        'result': True,
        'addition': {},
        'description': {}
    }


async def ping(request):
    answer = ANSWER.copy()
    answer.update({
        'description': {'message': 'pong'}
    })
    return web.json_response(answer)


async def get_accounts(request):
    # отдает все аккаунты из базы
    answer = ANSWER.copy()
    async with request.app['db'].acquire() as conn:
        query = text('SELECT * FROM accounts;')
        accounts = [list(x) for x in await conn.fetch(query)]
    if len(accounts) == 0:
        # если нет аккаунтов
        message = 'No accounts in base.'
        answer.update({
            'result': False,
            'description': {'message': message},
            'addition': {'accounts': accounts}
        })
        return web.json_response(answer)
    message = 'Accounts:\n'
    for acc in accounts:
        acc[0] = str(acc[0])
        status = 'open' if acc[4] else 'closed'

        message += (
            f'UUID - {acc[0]} | '
            f'name - {acc[1]} | '
            f'balance - {acc[2]} | '
            f'hold - {acc[3]} | '
            f'status - {status}.\n'
        )
    answer.update({
        'addition': {'accounts': accounts},
        'description': {'message': message}
    })
    return web.json_response(answer)


async def add_balance(request):
    answer = ANSWER.copy()
    data = json.loads(await request.text())
    uuid = data['uuid']
    balance = data['balance']
    async with request.app['db'].acquire() as conn:
        if not await check_uuid(conn, uuid):
            message = f'Account {uuid} doesn\'t exist.'
            answer.update({
                'result': False,
                'description': {'message': message},
            })
            return web.json_response(answer)
        # проверяем статус аккаунта, если открыт, то добавляем деньги
        status_query = text(f'SELECT status FROM accounts WHERE uuid=\'{uuid}\';')
        status = (await conn.fetch(status_query))[0]['status']
        if not status:
            # статус "закрыт""
            message = 'Account\'s status is "closed".'
            answer.update({
                'result': False,
                'description': {'message': message},
            })
            return web.json_response(answer)
        update_query = text(f'UPDATE accounts SET balance=balance + {balance} WHERE uuid=\'{uuid}\';')
        result = await conn.fetch(update_query)
        select_query = text(f'SELECT balance FROM accounts WHERE uuid=\'{uuid}\';')
        new_balance = (await conn.fetch(select_query))[0]['balance']
    message = f'New balance for account {uuid} is {new_balance}.'
    answer.update({
        'description': {'message': message},
        'addition': {'balance': new_balance}
    })
    return web.json_response(answer)


async def substract_balance(request):
    answer = ANSWER.copy()
    data = json.loads(await request.text())
    uuid = data['uuid']
    sub_balance = int(data['balance'])
    async with request.app['db'].acquire() as conn:
        if not await check_uuid(conn, uuid):
            message = f'Account {uuid} doesn\'t exist.'
            answer.update({
                'result': False,
                'description': {'message': message},
            })
            return web.json_response(answer)
        query = text(f'SELECT balance, hold, status FROM accounts WHERE uuid=\'{uuid}\';')
        (result,) = await conn.fetch(query)
        balance, hold, status = result.values()
        if not status:
            message = f'Account\'s status is "closed".'
            answer.update({
                'result': False,
                'description': {'message': message},
            })
            return web.json_response(answer)
        if balance < hold + int(sub_balance):
            message = f'Not enough money to substract. Current balance - {balance}.'
            answer.update({
                'result': False,
                'addition': {'balance': balance},
                'description': {'message': message},
            })
            return web.json_response(answer)
        balance -= (hold + sub_balance)
        query = text(f'UPDATE accounts SET balance={balance} WHERE uuid=\'{uuid}\';')
        result = await conn.fetch(query)
    message = f'New balance for account {uuid} is {balance}.'
    answer.update({
        'addition': {'balance': balance},
        'description': {'message': message},
    })
    return web.json_response(answer)


class StatusView(web.View):
    async def get(self):
        answer = ANSWER.copy()
        data = json.loads(await self.request.text())
        uuid = data['uuid']
        name = data['name']
        async with self.request.app['db'].acquire() as conn:
            if name is None:
                query = text(f'SELECT * FROM accounts WHERE uuid=\'{uuid}\';')
            else:
                query = text(f'SELECT * FROM accounts WHERE name LIKE \'%{name}%\';')
            accounts = await conn.fetch(query)
            if len(accounts) == 0:
                message = 'No matches in base.'
                answer.update({
                    'description': {'message': message},                    
                })
                return web.json_response(answer)
        addition = {}
        addition['accounts'] = []
        message = 'Found accounts:\n'
        for acc in accounts:
            uuid, name, balance, hold, status = acc.values()
            addition['accounts'].append({
                'uuid': str(uuid),
                'name': name,
                'balance': balance,
                'hold': hold,
                'status': status
            })
            status_type = 'open' if status else 'closed'
            message += (
                f'UUID - {acc[0]} | '
                f'name - {acc[1]} | '
                f'balance - {acc[2]} | '
                f'hold - {acc[3]} | '
                f'status - {status_type}.\n'
            )
        answer.update({ 
            'addition': addition,
            'description': {'message': message},
        })
        return web.json_response(answer)

    async def post(self):
        answer = ANSWER.copy()
        data = json.loads(await self.request.text())
        try:
            column = 'balance'
            int(data['balance'])
            column = 'hold'
            int(data['hold'])
            column = 'name'
            str(data['name'])
            column = 'status'
            if not (data['status'] is True or data['status'] is False):
                raise ValueError
        except ValueError:
            message = f'Wrong format for "{column}" column.'
            answer.update({
                'status': 500,
                'result': False,
                'addition': {'value': data[column], 'column': column},
                'description': {'message': message},
            })
            return web.json_response(answer)
        async with self.request.app['db'].acquire() as conn:
            uuid = str(await get_unique_uuid(conn))
            query = text(
                f'INSERT INTO accounts VALUES('
                f'\'{uuid}\','
                f'\'{data["name"]}\','
                f'{data["balance"]},'
                f'{data["hold"]},'
                f'{data["status"]});'
            )
            result = await conn.fetch(query)
            message = f'Account was created successfully.\nGenerated UUID: {uuid}'
        answer.update({
            'addition': {'uuid': uuid},
            'description': {'message': message},
        })
        return web.json_response(answer)

    async def put(self):
        answer = ANSWER.copy()
        data = json.loads(await self.request.text())
        uuid = data["uuid"]
        async with self.request.app['db'].acquire() as conn:
            if not await check_uuid(conn, uuid):
                message = f'Account {uuid} doesn\'t exist.'
                answer.update({
                    'result': False,
                    'description': {'message': message},
                })
                return web.json_response(answer)
            query = text(f'UPDATE accounts SET status=true WHERE uuid=\'{uuid}\';')
            result = await conn.fetch(query)
        message = f'{uuid} account\'s status now is "open".'
        answer.update({
            'description': {'message': message},
        })
        return web.json_response(answer)

    async def delete(self):
        answer = ANSWER.copy()
        data = json.loads(await self.request.text())
        uuid = data["uuid"]
        async with self.request.app['db'].acquire() as conn:
            if not await check_uuid(conn, uuid):
                message = f'Account {uuid} doesn\'t exist.'
                answer.update({
                    'result': False,
                    'description': {'message': message},
                })
                return web.json_response(answer)
            query = text(f'UPDATE accounts SET status=false WHERE uuid=\'{uuid}\';')
            result = await conn.fetch(query)
        message = f'{uuid} account\'s status now is "closed".'
        answer.update({
            'description': {'message': message},
        })
        return web.json_response(answer)
