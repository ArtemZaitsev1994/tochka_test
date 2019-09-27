import aiohttp
import asyncio
import json
import uuid as uuid_module
from utils import confirm_data, input_digit, input_uuid, is_uuid


HOST = 'http://0.0.0.0:8080'
ERROR_MESS = 'Something went wrong, try to ping server.'


def query_decor(link, method):
    def wrap(func):
        async def wrap_func(session):
            data = await func(session)
            if data is None:
                return
            print(method)
            async with session.request(method, link, json=data) as req:
                if req.status == 200:
                    data = json.loads(await req.text())
                    message = data['description']['message']
                    print('----------ANSWER----------')
                    print(message)
                    print('--------------------------')
                else:
                    print(ERROR_MESS)
        return wrap_func
    return wrap


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            print('''
    Available commands:
    ping server -                              1
    show all accounts -                        2
    add some money to user's balance -         3
    substract some money from user's balance - 4
    check status by users's name or uuid -     5
    create new account -                       6
    delete an account -                        7
    activate an account -                      8
            ''')
            command = input('Enter command: ')
            if command == '1':
                await ping_server(session)
            if command == '2':
                await show_all_accounts(session)
            if command == '3':
                await add_balance(session)
            if command == '4':
                await substract_balance(session)
            if command == '5':
                await check_status(session)
            if command == '6':
                await create_account(session)
            if command == '7':
                await disable_account(session)
            if command == '8':
                await activate_account(session)


async def ping_server(session):
    try:
        async with session.get(f'{HOST}/api/ping') as req:
            if req.status == 200:
                data = json.loads(await req.text())
                print('--------------------------')
                print('Server is available.')
                print(data['description']['message'])
                print('--------------------------')
    except aiohttp.client_exceptions.ClientConnectorError:
        print('----------ANSWER----------')
        print('Server is not available.')
        print('--------------------------')


@query_decor(f'{HOST}/api/accounts', 'get')
async def show_all_accounts(session):
    return True


@query_decor(f'{HOST}/api/add', 'post')
async def add_balance(session):
    uuid = input_uuid()
    if uuid == '':
        return
    balance = input_digit('balance')
    if balance == 0:
        return
    data = {
        'uuid': uuid,
        'balance': int(balance)
    }
    data_for_confirm = f'Do you want to add {balance} to {uuid}?'
    if not confirm_data(data_for_confirm):
        return
    return data


@query_decor(f'{HOST}/api/substract', 'post')
async def substract_balance(session):
    uuid = input_uuid()
    if uuid == '':
        return
    balance = input_digit('balance')
    if balance == 0:
        return
    data = {
        'uuid': uuid,
        'balance': int(balance)
    }
    data_for_confirm = f'Do you want to substract {balance} form {uuid}?'
    if not confirm_data(data_for_confirm):
        return
    return data

@query_decor(f'{HOST}/api/status', 'get')
async def check_status(session):
    uuid, name = input('Enter user\'s uuid or name: '), None
    if not is_uuid(uuid):
        name, uuid = uuid, None
    data = {
        'uuid': uuid,
        'name': name
    }
    return data


@query_decor(f'{HOST}/api/status', 'post')
async def create_account(session):
    name = input('Enter user\'s name: ')
    balance = input_digit('balance')
    if balance == 0:
        return
    hold = 0
    print('Do you want to enter hold?')
    if confirm_data():
        hold = input_digit('hold')
    status = True
    data = {
        'name': name,
        'balance': balance,
        'hold': hold,
        'status': status
    }
    data_for_confirm = f'''
        Do you want to create an account with:
        name:            {name}
        balance:         {balance}
        hold:            {hold}
        status:          open
        ?'''
    if not confirm_data(data_for_confirm):
        return
    return data


@query_decor(f'{HOST}/api/status', 'delete')
async def disable_account(session):
    uuid = input_uuid()
    if uuid == '':
        return
    data = {'uuid': uuid}
    data_for_confirm = f'Do you want to disable account with uuid - {uuid}?'
    if not confirm_data(data_for_confirm):
        return
    return data


@query_decor(f'{HOST}/api/status', 'put')
async def activate_account(session):
    uuid = input_uuid()
    if uuid == '':
        return
    data = {'uuid': uuid}
    data_for_confirm = f'Do you want to activate account with uuid - {uuid}?'
    if not confirm_data(data_for_confirm):
        return
    return data


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
