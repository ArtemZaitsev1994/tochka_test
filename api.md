Ping сервера:
GET /api/ping

Пример ответа:
{
    'status': 200,
    'result': True,
    'addition': {},
    'description': {'message': 'pong'}
}
----------------------

Получение всех аккаунтов:
GET /api/accounts

Пример ответа:
{
    'status': 200,
    'result': True,
    'addition': {},
    'description': {
        'message': 'UUID - 931bd4fd-495b-406f-a229-44b60ddb4aa1 | name - asd | balance - 6 | hold - 0 | status - open.'
    }
}

Ответ, если записей не существует:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'No accounts in base.'
    }
}
----------------------

Добавить сумму к балансу:
POST /api/add
Content-Type: application/json

Пример данных:
{
    'uuid': 'value-1',
    'balance': 100
}
uuid - UUID аккаунта
balance - баланс, который нужно добавить

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {'balance': 2100},
    'description': {
        'message': 'New balance for account value-1 is 2100.'
    }
}

Пример ответа, если аккаунт заблокирован:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'Account's status is "closed".'
    }
}
----------------------

Вычесть сумму из баланса:
POST /api/add
Content-Type: application/json

Пример данных:
{
    'uuid': 'value-1',
    'balance': 100
}
uuid - UUID аккаунта
balance - баланс, который нужно списать

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {'balance': 1900},
    'description': {
        'message': 'New balance for account value-1 is 1900.'
    }
}

Пример ответа, если аккаунт заблокирован:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'Account's status is "closed".'
    }
}

Пример отрицательного ответа, если не хватает денег:
{
    'status': 200,
    'result': False,
    'addition': {'balance': 2000},
    'description': {
        'message': 'Not enough money to substract. Current balance - 2000.'
    }
}
----------------------

Запрос на опредленного аккаунта по UUID или по имени пользователя:
GET /api/status
Content-Type: application/json

Пример данных:
{
    'uuid': 'value-1',
    'name': None
}
uuid - UUID аккаунта (либо None)
name - имя пользователя (либо None)
***
Приходит либо имя, либо uuid
Если пришел uuid, то ищем по точному совпадению
Если пришло имя, то ищем все совпадения по имени
***

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {
        'accounts': [{
            'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1',
            'name': 'Ivan',
            'balance': 100,
            'hold': 10,
            'status': True
        }]
    },
    'description': {
        'message': 'Found accounts:
        UUID - 931bd4fd-495b-406f-a229-44b60ddb4aa1 | name - Ivan | balance - 100 | hold - 10 | status - open.'
    }
}

Пример ответа, если аккаунты не найдены:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'No matches in base.'
    }
}
----------------------

Создание аккаунта:
POST /api/status
Content-Type: application/json

Пример данных:
{
    'name': 'Ivan',
    'balance': 1000,
    'hold': 10,
    'status': True
}
name - имя пользователя (либо None)
balance - баланс аккаунта
hold - сумма вычета
status - статус аккаунта (по умолчанию True)

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {
        'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1'
    },
    'description': {
        'message': 'Account was created successfully.\nGenerated UUID: 931bd4fd-495b-406f-a229-44b60ddb4aa1'
}

Пример ответа, с неверными типами:
{
    'status': 500,
    'result': False,
    'addition': {
        'value': 'qwerty',
        'column': 'balance'
    },
    'description': {
        'message': 'Wrong format for "balance" column.'
    }
}
----------------------

Смена статуса аккаунта на "open":
PUT /api/status
Content-Type: application/json

Пример данных:
{
    'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1'
}
uuid - UUID аккаунта

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {
        'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1'
    },
    'description': {
        'message': '931bd4fd-495b-406f-a229-44b60ddb4aa1 account\'s status now is "open".'
}

Пример ответа, с неверными типами:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'Account {uuid} doesn\'t exist.'
    }
}
----------------------

Смена статуса аккаунта на "closed":
DELETE /api/status
Content-Type: application/json

Пример данных:
{
    'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1'
}
uuid - UUID аккаунта

Пример успешного ответа:
{
    'status': 200,
    'result': True,
    'addition': {
        'uuid': '931bd4fd-495b-406f-a229-44b60ddb4aa1'
    },
    'description': {
        'message': '931bd4fd-495b-406f-a229-44b60ddb4aa1 account\'s status now is "closed".'
}

Пример ответа, с неверными типами:
{
    'status': 200,
    'result': False,
    'addition': {},
    'description': {
        'message': 'Account {uuid} doesn\'t exist.'
    }
}
