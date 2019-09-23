from server import (
    ping,
    get_accounts,
    add_balance,
    substract_balance,
    StatusView
)

routes = [
    ('GET', '/api/ping', ping, 'ping'),
    ('GET', '/api/accounts', get_accounts, 'get_accounts'),
    ('POST', '/api/add', add_balance, 'add_balance'),
    ('POST', '/api/substract', substract_balance, 'substract_balance'),
    ('*', '/api/status', StatusView, 'StatusView'),
]