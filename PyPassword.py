# -*- coding: utf-8 -*-
import base64
import os
import random
import sqlite3
import string
import sys
from getpass import getpass

import pyperclip
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Color:
    # Sources:
    # https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
    # http://ascii-table.com/ansi-escape-sequences.php
    # PURPLE = '\033[95m'
    # CYAN = '\033[96m'
    # DARKCYAN = '\033[36m'
    # BLUE = '\033[94m'
    # GREEN = '\033[92m'
    # YELLOW = '\033[93m'
    # RED = '\033[91m'
    # BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Program:
    name = 'Python Password'  # Work in progress
    version = '0.1'  # Alpha
    author = 'Jakub S.'
    git_hub = 'https://github.com/AnonymousX86/Python-Password'


def header():
    foo = ''
    for i in range(len(Program.name) + len(Program.version) + 10):
        foo += '-'
    foo += '\n' + \
           f'+++ {Program.name} v{Program.version} +++\n'
    for i in range(len(Program.name) + len(Program.version) + 10):
        foo += '-'
    foo += '\n'
    return foo


def mark(txt: str):
    """Underlines text"""
    return Color.UNDERLINE + txt + Color.END


def clear():
    """Clears console (Windows only)."""
    os.system('cls')


def confirm():
    input('\n---\n\nPress ENTER to continue...')


def show_records(records=None):
    # Default query - passwords' names
    if records is None:
        records = query('SELECT `name` FROM `passwords`;')

    if not records:
        print('Nothing to show!')

    else:
        for record in records:
            print(f'- {record[0]}\n')


def check_files():
    """Checking if database and key file exists. If not - creates them."""
    print('Checking files integrity...')

    # Settings file
    try:
        open(file('salt.key'), 'rb')
    except FileNotFoundError:
        print('Settings file not found! Creating one...')
        open(file('salt.key'), 'x')

        custom_salt = input(
            'Provide custom salt or leave empty for random (it should be super secret and super safe): ')
        if custom_salt == '':
            custom_salt = os.urandom(16)

        else:
            custom_salt.encode()

        with open(file('salt.key'), 'wb') as f:
            f.write(custom_salt)
    finally:
        print('Settings OK!')

    # Database
    try:
        open(file('passwords.db'), 'rb')
    except FileNotFoundError:
        print('Database file not found! Creating one...')
        open(file('passwords.db'), 'x')
        query('''create table passwords(id INTEGER constraint passwords_pk primary key autoincrement, name varchar not
        null, password varchar not null );''')
        query('create unique index passwords_name_uindex on passwords (name);')
    finally:
        print('Database OK!')

    # ``key`` file
    try:
        open(file('master.key'), 'r')
    except FileNotFoundError:
        print('Key file not found! Creating one...')
        generate_key()
    finally:
        print('Key OK!')


def file(filename: str):
    """
    Add absolute path to file name.
    :param filename: File name.
    :return: Absolute path to file with specified name.
    """
    return os.path.join(os.path.dirname(__file__), filename)


def query(q_input: str, q_args=None):
    """
    Executes query in SQLite database.
    :param q_input: SQL query.
    :param q_args: Query arguments (``?`` symbol for placeholders).
    :return: All records or ``None``.
    """
    if q_args is None:
        q_args = []
    conn = sqlite3.connect(file('passwords.db'))
    c = conn.cursor()
    c.execute(q_input, q_args)
    records = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return records


def rand_password(length: int = 16):
    """
    Most safely password.
    :param length: Password length (default: 16).
    :return: Very safe password.
    """
    possibilities = list(str(string.ascii_letters + string.digits + string.punctuation))
    result = ''
    for i in range(length):
        result += random.choice(possibilities)
    return result


# Option 1
def generate_key():
    password_input = input('Provide master password: ')
    password = password_input.encode()

    try:
        open(file('salt.key'), 'rb')

    except FileNotFoundError:
        print('No settings are found! Please restart the program, so it could create them for you')
        confirm()

    else:
        with open(file('salt.key'), 'rb') as f:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=f.read(),
                iterations=100000,
                backend=default_backend()
            )

        key = base64.urlsafe_b64encode(kdf.derive(password))

        try:
            with open(file('master.key'), 'wb') as f:
                f.write(key)
        except FileNotFoundError:
            print('File removed! Please do not remove it!')
        else:
            print('Key file generated')


# Option 2
def get_password():
    print('Available passwords:\n')
    show_records()

    password_input = input('>>> ')
    if password_input.lower() in ('', 'cancel'):
        return

    else:
        to_decrypt = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])[0][0]
        if (n := type(to_decrypt)) is not None:
            if n is bytes:
                with open(file('master.key'), 'rb') as f:
                    key = f.read()
                    f = Fernet(key)

                    try:
                        pyperclip.copy(str(f.decrypt(to_decrypt).decode('utf-8')))
                    except InvalidToken:
                        print('You do not have permissions to see that password,'
                              ' please re-generate key with matching master password and salt.')
                    else:
                        print('Password copied to clipboard!')
            else:
                raise SyntaxError('Bad password type, that\'s an error.')
        else:
            raise KeyError('That password does not exits')


# Option 3
def set_password():
    password_name = input('Provide password name (visible): ')
    password_value = getpass('Provide password value (or leave empty for random): ')

    if password_value == '':
        password_value = rand_password()

    with open(file('master.key'), 'rb') as f:
        key = f.read()
        f = Fernet(key)
        password_encrypted = f.encrypt(password_value.encode())

    try:
        query('INSERT INTO passwords (`name`, `password`) VALUES (?, ?);', [password_name, password_encrypted])

    except sqlite3.IntegrityError:
        print('That password already exists!')


# Option 4
def del_password():
    print('Available passwords:\n')
    show_records()

    password_input = input('>>> ')
    if password_input != '':
        to_del = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])[0][0]
        if (n := type(to_del)) is not None:
            if n is bytes:
                del_confirm = input('If you want to proceed, please type once more password name: ')

                if password_input == del_confirm:
                    query('DELETE FROM `passwords` WHERE `name` LIKE ?;', [password_input])

                else:
                    print('Action cancelled')
            else:
                raise SyntaxError('Bad password type, that\'s an error')
        else:
            raise KeyError('That password does not exits')
    else:
        print('Action cancelled')


# Option 5
def quick_start():
    print(f'Program name:    {Program.name}\n'
          f'Current version: {Program.version}\n'
          f'Author:          {Program.author}\n'
          f'GitHub:          {Program.git_hub}')


if __name__ == '__main__':
    clear()
    check_files()
    while True:
        clear()
        print(
            header(),
            ' Select option:\n'
            ' 1. {0}e-generate master key\n'
            ' 2. {1}et password\n'
            ' 3. {2}ave password\n'
            ' 4. {3}elete password\n'
            ' 5. {4}nfo\n'
            ' 0. {5}xit'.format(
                # Options' numbers
                mark('R'),  # 1
                mark('G'),  # 2
                mark('S'),  # 3
                mark('D'),  # 4
                mark('I'),  # 5
                mark('E')  # 0
            ))
        choice = input('>>> ')

        clear()

        if choice in ('1', 'R', 'r'):
            generate_key()

        elif choice in ('2', 'G', 'g'):
            get_password()

        elif choice in ('3', 'S', 's'):
            set_password()

        elif choice in ('4', 'D', 'd'):
            del_password()

        elif choice in ('5', 'H', 'h'):
            quick_start()

        elif choice in ('0', 'E', 'e'):
            clear()
            print(f' * Thanks for using {Program.name}! *')
            confirm()
            sys.exit()

        confirm()
