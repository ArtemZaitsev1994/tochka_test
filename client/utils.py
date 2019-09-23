from uuid import UUID

def confirm_data(data: str = '') -> bool:
    # функция подтверждения введенных данных
    flag = ''
    if data != '':
        flag = input(f'Confirm your data: {data}\n(yes/no): ')
    while flag.lower() not in ('yes', 'no'):
        flag = input('please enter "yes" or "no": ')
    if flag.lower() == 'yes':
        return True
    if data != '':
        print('Command was canceled')
    return False


def input_uuid() -> str:
    # ввод uuid в верном формате
    uuid = input('Enter user\'s uuid: ')
    while True:
        try:
            if uuid == str(UUID(uuid, version=4)):
                return uuid
        except ValueError:
            pass
        uuid = input('Wrong UUIDv4 format, try again (enter "exit" for exit): ')
        if uuid == 'exit':
            return ''


def input_digit(item: str) -> int:
    # ввод числа
    value = input(f'Enter user\'s {item}: ')
    while True:
        try:
            return int(value)
        except ValueError:
            pass
        value = input('Value should be numeric, try again (enter "0" for exit): ')
        if value == '0':
            return 0


def is_uuid(uuid: str) -> bool:
    # проверка на верный формат uuid
    try:
        if uuid == str(UUID(uuid, version=4)):
            return True
    except ValueError:
        return False
