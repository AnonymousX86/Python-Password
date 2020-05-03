# -*- coding: utf-8 -*-
"""
Simple Python console app for storing passwords.
"""
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
    """
    Python specified values used for text formatting.
    """
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
    """
    Infos about the program.
    """
    name = 'Python Password'  # Work in progress
    version = '0.1.1'  # Alpha
    author = 'Jakub S.'
    git_hub = 'https://github.com/AnonymousX86/Python-Password'
    icon = 'Icon made by Freepik from www.flaticon.com'


class File:
    """
    Names for program files.
    """
    alpha_key = 'Alpha.key'
    beta_key = 'Beta.key'
    sqlite = 'Passwords.db'


def header():
    """
    Shows welcome text.
    :return: Formatted text.
    """
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
    """
    Underlines text.
    :param txt: Text to underline.
    :return: Underlined text.
    """
    return Color.UNDERLINE + txt + Color.END


def clear():
    """
    Clears the console. For now Windows (NT) only.
    """
    os.system('cls')


def confirm():
    """
    Prints confirmation and waits for ENTER to be pressed.
    """
    input('\n---\n\nPress ENTER to continue...')


def show_records(records=None):
    """
    Shows specified values from database.
    :param records: Records from SQL query to show. Default are passwords' names.
    """
    if records is None:
        records = query('SELECT `name` FROM `passwords`;')

    if not records:
        print('Nothing to show!')

    else:
        for record in records:
            print(f'- {record[0]}\n')


def missing_file(file_name: str):
    """
    Shows info about missing file.
    :param file_name: Name of missing file.
    """
    print(f'{file_name} file has removed while processing!\n'
          f'This file is needed for proper working.\n'
          f'Restart program to create one.')
    confirm()


def check_files():
    """
    Checking if all files exists.
    Missing files are being created.
    """
    print('Checking files integrity...')

    # Salt (beta password)
    try:
        open(file(File.beta_key))
    except FileNotFoundError:
        print('Beta password file not found! Creating one...')
        generate_salt()
    else:
        print(f'{File.beta_key} OK!')

    # SQLite database
    try:
        open(file(File.sqlite))
    except FileNotFoundError:
        print('Passwords database not found! Creating one...')
        generate_sqlite()
    else:
        print(f'{File.sqlite} OK!')

    # Master password (alpha password)
    try:
        open(file(File.alpha_key))
    except FileNotFoundError:
        print('Alpha password file not found! Creating one...')
        generate_master_key()
    else:
        print(f'{File.alpha_key} OK!')


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
    :param q_args: Query arguments (replaces ``?`` symbol in query).
    :return: All records or ``None`` if nothing is matching query.
    """
    if q_args is None:
        q_args = []
    conn = sqlite3.connect(file(File.sqlite))
    my_cursor = conn.cursor()
    my_cursor.execute(q_input, q_args)
    records = my_cursor.fetchall()
    conn.commit()
    my_cursor.close()
    conn.close()
    return records


def rand_password(length: int = 16):
    """
    Most safely password.
    :param length: Password length (default is 16).
    :return: Very safe password.
    """
    possibilities = list(str(string.ascii_letters + string.digits + string.punctuation))
    result = ''
    for i in range(length):
        result += random.choice(possibilities)
    return result


def generate_sqlite():
    """
    Creates SQLite database.
    """
    try:
        open(file(File.sqlite), 'x')
    except FileExistsError:
        print(f'Database already exists! Please remove it manually ({File.sqlite} file) and restart {Program.name}')
    else:
        query('''create table passwords(id INTEGER constraint passwords_pk primary key autoincrement, name varchar not
                 null, password varchar not null );''')
        query('create unique index passwords_name_uindex on passwords (name);')
        print('Database successfully created!')


def generate_salt():
    """
    Generates salt - Beta.key file.
    """
    try:
        open(file(File.beta_key), 'x')
    except FileExistsError:
        pass
    finally:
        custom_salt = getpass(
            'Provide custom beta password or leave empty for random (it should be super secret and super safe): ')
        if custom_salt == '':
            custom_salt = os.urandom(16)
        else:
            while True:
                salt_confirm = getpass('Confirm password: ')
                if salt_confirm == custom_salt:
                    break
                elif salt_confirm in ('c', 'cancel'):
                    print('Action cancelled!')
                    return
                else:
                    print('Passwords do not match')
            custom_salt.encode()
        try:
            with open(file(File.beta_key), 'wb') as f:
                f.write(custom_salt)
        except FileNotFoundError:
            missing_file(File.beta_key)
        else:
            print('Beta password created successfully!')


# Option 1
def generate_master_key():
    """
    Generates hashing password based on user input and salt.
    """
    try:
        open(file(File.beta_key), 'rb')
    except FileNotFoundError:
        missing_file(File.beta_key)
    else:
        while True:
            password_input = input('Provide alpha password: ')
            if len(password_input) < 6:
                print('Password should be 6 characters long')
            else:
                break
        password = password_input.encode()
        try:
            with open(file(File.beta_key), 'rb') as f:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=f.read(),  # Beta password is just salt
                    iterations=100000,
                    backend=default_backend()
                )
        except FileNotFoundError:
            missing_file(File.beta_key)
        else:
            key = base64.urlsafe_b64encode(kdf.derive(password))
            try:
                with open(file(File.alpha_key), 'wb') as f:
                    f.write(key)
            except FileNotFoundError:
                missing_file(File.alpha_key)
            else:
                print('Alpha key created successfully!')


# Option 2
def get_password():
    """
    Decrypts password from database and saves it to clipboard.
    If key is missing or it doesn't match password's source, only warning is showed on the screen.
    """
    print('Available passwords:\n')
    show_records()

    password_input = input('Choose: ')
    if password_input.lower() in ('', 'cancel'):
        return

    else:
        to_decrypt = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])[0][0]
        if (n := type(to_decrypt)) is not None:
            if n is bytes:
                with open(file(File.alpha_key), 'rb') as f:
                    key = f.read()
                    f = Fernet(key)

                    try:
                        pyperclip.copy(str(f.decrypt(to_decrypt).decode('utf-8')))
                    except InvalidToken:
                        print('You do not have permissions to see that password,'
                              ' please re-generate keys with matching alpha and beta passwords.')
                    else:
                        print('Password copied to clipboard!')
            else:
                print('Bad password type, that\'s a critical error.')
        else:
            print('That password does not exits')


# Option 3
def set_password():
    """
    Encrypts and saves password to database.
    """
    while True:
        password_name = input('Provide password name (visible): ')
        if len(password_name) < 4:
            print('Password alias should be at least 4 characters long')
        else:
            break
    password_value = getpass('Provide password (or leave empty for random): ')
    if password_value == '':
        password_value = rand_password()
    try:
        with open(file(File.alpha_key), 'rb') as f:
            key = f.read()
            f = Fernet(key)
            password_encrypted = f.encrypt(password_value.encode())
    except FileNotFoundError:
        missing_file(File.alpha_key)
    else:
        try:
            query('INSERT INTO passwords (`name`, `password`) VALUES (?, ?);', [password_name, password_encrypted])
        except sqlite3.IntegrityError:
            print('That password already exists!')
        else:
            print('Password saved successfully!')


# Option 4
def del_password():
    """
    Deletes password from database, require confirmation.
    """
    print('Available passwords:\n')
    show_records()

    password_input = input('Choose: ')

    if password_input not in ('', 'c', 'cancel'):
        to_del = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])[0][0]
        if (proper_type := type(to_del)) is not None:
            if proper_type is bytes:
                del_confirm = input('If you want to proceed, please type once more password name: ')

                while True:
                    if password_input == del_confirm:
                        query('DELETE FROM `passwords` WHERE `name` LIKE ?;', [password_input])
                        break

                    elif del_confirm in ('c', 'cancel'):
                        print('Action cancelled')
                        break

                    else:
                        print('Passwords do not match')
                        del_confirm = input('Try once more: ')
            else:
                print('Bad password type, that\'s a critical error')
        else:
            print('That password does not exists')
    else:
        print('Action cancelled')


# Option 5
def quick_start():
    """
    Shows general info about the program.
    """
    print(f' Program name:    {Program.name}\n'
          f' Current version: {Program.version}\n'
          f' Author:          {Program.author}\n'
          f' GitHub:          {Program.git_hub}\n'
          f' Icon:            {Program.icon}\n'
          f'\n'
          f' All useful info can be found on GitHub.')


if __name__ == '__main__':
    clear()
    check_files()
    while True:
        clear()
        print(
            header(),
            ' Select option:\n'
            ' 1. Change {0}lpha password\n'  # alpha
            ' 2. {1}et password\n'  # Get
            ' 3. {2}et password\n'  # Set
            ' 4. {3}elete password\n'  # Delete
            ' 5. {4}nfo\n'  # Info
            ' 0. E{5}it'.format(  # Exit
                # Options' numbers
                mark('a'),  # 1
                mark('G'),  # 2
                mark('S'),  # 3
                mark('D'),  # 4
                mark('I'),  # 5
                mark('x')  # 0
            ))
        choice = input('Choose: ')

        clear()

        if (c := choice.lower()) in ('1', 'a'):
            generate_master_key()

        elif c in ('2', 'g'):
            get_password()

        elif c in ('3', 's'):
            set_password()

        elif c in ('4', 'd'):
            del_password()

        elif c in ('5', 'i'):
            quick_start()

        elif c in ('0', 'x'):
            clear()
            print(f' * Thanks for using {Program.name}! *')
            confirm()
            sys.exit()

        confirm()
