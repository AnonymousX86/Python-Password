# -*- coding: utf-8 -*-
"""
Simple Python console app for storing passwords.
"""
import base64
import os
import random
import sqlite3
import string

import kivy
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from kivy import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput


def foo():
    """Blank function."""
    pass


class Color:
    """
    Python specified values used for text formatting.

    Sources:
        https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
        http://ascii-table.com/ansi-escape-sequences.php
    """
    # PURPLE = '\033[95m'
    # CYAN = '\033[96m'
    # DARKCYAN = '\033[36m'
    # BLUE = '\033[94m'
    # GREEN = '\033[92m'
    # YELLOW = '\033[93m'
    # RED = '\033[91m'
    # BOLD = '\033[1m'
    # Above values are not in use (yet)
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Program:
    """
    Infos about the program.
    """
    name = 'Python Password'
    version = '0.2.0'
    author = 'Jakub S.'
    git_hub = 'https://github.com/AnonymousX86/Python-Password'
    icon = 'Icon made by Freepik from www.flaticon.com'
    rd_party = '  - UPX\n' \
               '  - Kivy'


class File:
    """
    Names for program's files.
    """
    alpha_key = 'Alpha.key'
    beta_key = 'Beta.key'
    sqlite = 'Passwords.db'


class MyPopup:
    def __init__(self,
                 # Values specified per popup
                 title='Warning!',
                 description='Wild exception has appeared.',
                 dismiss='OK', after=foo, is_password=False,
                 min_input=6,

                 # Safe values for each popup
                 popup_size=250, btn_size=(.5, .3),
                 center_x_pos=None, sep_size=(1, .2),
                 label_size=(.7, .6), input_size=(.7, .2), ):

        # Mutable argument
        if center_x_pos is None:
            center_x_pos = {'center_x': 0.5}

        # Configurable arguments
        self.title = title
        self.description = description
        self.dismiss = dismiss
        self.after = after
        self.is_password = is_password
        self.min_input = min_input

        # Arguments that shouldn't be changes
        self.popup_size = popup_size
        self.btn_size = btn_size
        self.center_x_pos = center_x_pos
        self.sep_size = sep_size
        self.label_size = label_size
        self.input_size = input_size

        # Value that CAN'T be changed
        self._input = None

    def sep(self):
        return Label(size_hint=self.sep_size)

    def save_input(self, value):
        if len(value) < self.min_input:
            error_popup = MyPopup(
                title='Error!',
                description=f'This should be at least {self.min_input} characters long'
            ).default_popup()
            error_popup.open()
        else:
            self._input = value
            self.after()

    def get_input(self):
        return self._input

    def default_popup(self):
        default_data = BoxLayout(orientation='vertical')
        default_data.add_widget(Label(
            text=self.description, size_hint=self.label_size,
            pos_hint=self.center_x_pos, markup=True))
        default_data.add_widget(self.sep())
        default_data.add_widget(Label(size_hint=self.input_size))
        default_data.add_widget(Button(
            text=self.dismiss, on_press=lambda a: default_popup.dismiss(),
            size_hint=self.btn_size, pos_hint=self.center_x_pos))
        default_popup = Popup(
            title=self.title,
            content=default_data,
            size_hint=(None, None),
            size=(self.popup_size * 1.61, self.popup_size),
            auto_dismiss=True,
            on_dismiss=lambda a: self.after()
        )
        return default_popup

    def input_popup(self):
        input_data = BoxLayout(orientation='vertical')
        input_data.add_widget(Label(
            text=self.description, size_hint=self.label_size,
            pos_hint=self.center_x_pos, markup=True))
        popup_input = TextInput(
            id='text_input_popup', password=self.is_password,
            size_hint=self.input_size, pos_hint=self.center_x_pos,
            multiline=False)
        input_data.add_widget(popup_input)
        input_data.add_widget(self.sep())
        input_data.add_widget(Button(
            text=self.dismiss, on_press=lambda a: input_popup.dismiss(),
            size_hint=self.btn_size, pos_hint=self.center_x_pos))
        input_popup = Popup(
            title=self.title,
            content=input_data,
            size_hint=(None, None),
            size=(self.popup_size * 1.61, self.popup_size),
            auto_dismiss=True,
            on_dismiss=lambda a: self.save_input(popup_input.text)
        )
        return input_popup


def file(filename: str, file_type='u'):
    """
    Add absolute path to file name. Linking to AppData/Local or files next to ``.exe`` file.
    :param filename: File to access name.
    :param file_type: Is file program or user related.
    :return: Absolute path to file with specified name.
    """
    # Program files
    if file_type == 'p':
        return os.path.join(os.path.dirname(__file__), f'PyPassword_data/{filename}')
    # User files
    elif file_type == 'u':
        return os.path.join(os.path.dirname(__file__), f'{os.getenv("LOCALAPPDATA")}/PyPassword/{filename}')


def query(q_input: str, q_args=None):
    """
    Executes query in SQLite database.
    :param q_input: SQL query.
    :param q_args: Query arguments (replaces ``?`` symbol in query).
    :return: All records or ``None`` if nothing is matching query.
    """
    if q_args is None:
        q_args = []
    try:
        open(file(File.sqlite))
    except FileNotFoundError:
        generate_sqlite()
    finally:
        with sqlite3.connect(file(File.sqlite)) as conn:
            my_cursor = conn.cursor()
            try:
                my_cursor.execute(q_input, q_args)
            except sqlite3.OperationalError:
                generate_sqlite()
                return None
            else:
                Logger.info('Database: Accessing SQLite with query:')
                Logger.info(f'Database: "{q_input}".')
                if q_args:
                    Logger.info('Database: With arguments:')
                    Logger.info(f'Database: "{q_args}".')
                records = my_cursor.fetchall()
                conn.commit()
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


def generate_appdata():
    """
    Creates ``PyPassword`` folder in local app data.
    """
    os.system('cd %localappdata% && md PyPassword')


def generate_sqlite():
    """
    Creates SQLite database.
    """
    try:
        generate_appdata()
        open(file(File.sqlite), 'x')
    except FileExistsError:
        pass
    else:
        Logger.warning('Database: SQLite not found, creating it.')
    finally:
        query('''create table passwords(id INTEGER constraint passwords_pk primary key autoincrement, name varchar not
                 null, password varchar not null );''')
        query('create unique index passwords_name_uindex on passwords (name);')


def generate_salt():
    """
    Generates salt - Beta.key file.
    """
    try:
        generate_appdata()
        open(file(File.beta_key), 'x')
    except FileExistsError:
        pass
    else:
        Logger.warning('Structure: Salt file, creating it.')
    finally:
        custom_salt = os.urandom(16)
        with open(file(File.beta_key), 'wb') as f:
            f.write(custom_salt)


# def get_password():
#     password_input = _input(' Choose: ')
#     if password_input.lower() in ('', 'cancel'):
#         return
#
#     else:
#         try:
#             to_decrypt = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])
#         except FileNotFoundError:
#             pass
#         else:
#             n = type(to_decrypt)
#             if n is not None:
#                 to_decrypt = to_decrypt[0][0]
#                 if n is bytes:
#                     with open(file(File.alpha_key), 'rb') as f:
#                         key = f.read()
#                         f = Fernet(key)
#                         try:
#                             pyperclip.copy(str(f.decrypt(to_decrypt).decode('utf-8')))
#                         except InvalidToken:
#                             print(' You do not have permissions to see that password,\n'
#                                   ' please re-generate keys with matching alpha and beta passwords')
#                         else:
#                             print(' Password copied to clipboard!')
#                 else:
#                     print(' Bad password file_type, that\'s a critical error')
#             else:
#                 print(' That password does not exits')
#
#
# def del_password():
#     if password_input not in ('', 'c', 'cancel'):
#         to_del = query('SELECT `password` FROM `passwords` WHERE `name` LIKE ?;', [password_input])
#         if to_del is not None:
#             to_del = to_del[0][0]
#             if type(to_del) is bytes:
#                 del_confirm = _input(' If you want to proceed, please file_type once more password name: ')
#                 while True:
#                     if password_input == del_confirm:
#                         try:
#                             query('DELETE FROM `passwords` WHERE `name` LIKE ?;', [password_input])
#                         except FileNotFoundError:
#                             pass
#                         else:
#                             print('Password deleted successfully!')
#                         finally:
#                             break
#
#                     elif del_confirm in ('c', 'cancel'):
#                         print(' Action cancelled')
#                         break
#
#                     else:
#                         print(' Passwords do not match')
#                         del_confirm = _input('Try once more: ')
#             else:
#                 print(' Bad password file_type, that\'s a critical error')
#         else:
#             print(' That password does not exists')
#     else:
#         print(' Action cancelled')


def encrypt(text):
    """
    Encrypts provided text with alpha password.
    :param text: Text to encrypt.
    :return: Encrypted text.
    """
    try:
        open(file(File.beta_key))
    except FileNotFoundError:
        print('Salt was not found, generating it.')
        generate_salt()
    finally:
        try:
            open(file(File.alpha_key))
        except FileNotFoundError:
            return None
        else:
            with open(file(File.alpha_key), 'rb') as f:
                key = f.read()
                f = Fernet(key)
                return f.encrypt(text.encode())


kivy.require('1.11.1')

Config.set('kivy', 'window_icon', file('icon.ico', 'p'))
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'exit_on_esc', 0)
Config.set('kivy', 'pause_on_minimize', 1)

Config.set('kivy', 'log_dir', file('./logs/', 'p'))
Config.set('kivy', 'log_enable', 1)
Config.set('kivy', 'log_level', 'error')
Config.set('kivy', 'log_name', 'PyPassword_%y-%m-%d_%_.txt')
Config.set('kivy', 'log_maxfiles', 30)

Builder.load_file(file('py_password.kv', 'p'))


class MenuScreen(Screen):
    title_size = 30
    title_text = '[b]Welcome to Python Password[/b]'
    btn_font = 20
    btn_width = .5
    btn_pos = {'center_x': .5}

    def goto_settings(self):
        print('Go to settings called')
        self.manager.transition.direction = 'left'
        self.manager.current = 'settings'

    def goto_get_password(self):
        print('Go to get password called')
        self.manager.transition.direction = 'left'
        self.manager.current = 'get_password'

    def goto_set_password(self):
        print('Go to set password called')
        self.manager.transition.direction = 'left'
        self.manager.current = 'set_password'

    def goto_del_password(self):
        print('Go to delete password called')
        self.manager.transition.direction = 'left'
        self.manager.current = 'del_password'

    def goto_info(self):
        print('Go to info called')
        self.manager.transition.direction = 'left'
        self.manager.current = 'info'

    def exit_program(self):
        print('Exit called')
        self.manager.transition.direction = 'right'
        App.get_running_app().stop()


class SettingsScreen(Screen):
    def back(self):
        print('Back called.')
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def submit(self):
        print('Submit called')
        min_len = 6
        if len(self.ids['alpha'].text) < min_len:
            alert_pop = MyPopup(
                title='Bad format!',
                description=f'Password should be at least {min_len} characters long.'
            ).default_popup()

        else:
            try:
                open(file(File.beta_key))
            except FileNotFoundError:
                generate_salt()
            finally:
                try:
                    open(file(File.alpha_key))
                except FileNotFoundError:
                    open(file(File.alpha_key), 'x')
                finally:
                    with open(file(File.beta_key), 'rb') as f:
                        kdf = PBKDF2HMAC(
                            algorithm=hashes.SHA256(),
                            length=32,
                            salt=f.read(),
                            iterations=100000,
                            backend=default_backend()
                        )
                    with open(file(File.alpha_key), 'wb') as f:
                        key = base64.urlsafe_b64encode(kdf.derive(self.ids['alpha'].text.encode()))
                        f.write(key)

                    alert_pop = MyPopup(
                        title='Success!',
                        description='Alpha password successfully saved!',
                        after=self.back
                    ).default_popup()

        alert_pop.open()


class GetPassword(Screen):
    passwords = 'Nothing to show.'
    db_empty = True

    def back(self):
        print('Back called.')
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def update_passwords(self):
        print('Update passwords called.')
        records = query('SELECT `name` FROM `passwords`;')
        if len(records) == 0:
            result = 'No passwords in database.'
            self.db_empty = True
        else:
            result = ''
            for record in records:
                result += f' - {record[0]}\n'
            self.db_empty = False
        self.ids['passwords_box'].text = result

    def get_password(self):
        print('Get password called')
        if self.db_empty is True:
            alert_pop = MyPopup(
                title='No passwords in database.',
                description='Please add at least one password to database.'
            ).default_popup()
        else:
            alert_pop = MyPopup(
                title='That won\'t work.',
                description='Function has work in progress status.'
            ).default_popup()
        alert_pop.open()


class SetPassword(Screen):
    _password_alias = None
    _password_value = None
    _input_popup = None

    Logger.debug('Database: Printing default query for passwords\' names')
    Logger.debug(f'Database: {query("SELECT `name` FROM `passwords`;")}')

    passwords_count = 'Program is storing {0} passwords.'.format(len(query('SELECT `name` FROM `passwords`;')))

    def back(self):
        print('Back called.')
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'

    def update_passwords(self):
        print('Update passwords called')
        self.passwords_count = 'Program is storing {0} passwords.'.format(len(query('SELECT `name` FROM `passwords`')))
        self.ids['passwords_count_label'].text = self.passwords_count

    def set_password(self):
        print('Set password called')
        self.save_alias()

    def files_ok(self):
        try:
            open(file(File.alpha_key))
        except FileNotFoundError:
            self._input_popup = MyPopup(
                title='Error!',
                description=f'Alpha password is not set. It is necessary\n'
                            f'to store passwords.\n'
                            f'To do this, go to settings menu.',
                after=self.back
            ).default_popup()
            self._input_popup.open()
        else:
            return True

    def save_alias(self):
        print('Save alias called.')
        if self.files_ok() is True:
            self._input_popup = MyPopup(
                title='Saving password',
                description='Provide password alias (visible name):',
                after=self.save_value,
                min_input=3
            )
            self._input_popup.input_popup().open()

    def save_value(self):
        self._password_alias = self._input_popup.get_input()
        print('Save value called.')
        self._input_popup = MyPopup(
            title='Saving password',
            description='Provide password:',
            after=self.confirm_save,
            is_password=True
        )
        self._input_popup.input_popup().open()

    def confirm_save(self):
        self._password_value = self._input_popup.get_input()

        try:
            query('INSERT INTO passwords (`name`, `password`) VALUES (?, ?);',
                  [self._password_alias, encrypt(self._password_value)])
        except sqlite3.IntegrityError:
            self._input_popup = MyPopup(
                title='Error!',
                description=f'Password [b]{self._password_alias}[/b] already exists!'
            ).default_popup()
        else:
            self._input_popup = MyPopup(
                title='Done!',
                description=f'Password [b]{self._password_alias}[/b] successfully saved!',
                after=self.back
            ).default_popup()
            Logger.info(f'Passwords: New password saved "{self._password_alias[:3]}***"')

        self._input_popup.open()


class DelPassword(Screen):
    def back(self):
        print('Back called.')
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'


class InfoScreen(Screen):
    info_text = \
        'Name:     {0.name}\n' \
        'Version:  {0.version}\n' \
        'Author:   {0.author}\n' \
        'GitHub:   {0.git_hub}\n' \
        'Icon:     {0.icon}\n' \
        '\n' \
        'Third party software:\n' \
        '{0.rd_party}\n' \
        '\n' \
        'All useful info can be found on GitHub.\n' \
        '\n' \
        'Remember, that any software to store your passwords won\'t be 100% safe,\n' \
        'only your head gives you full protection from leaks.'.format(Program)

    def back(self):
        print('Back called.')
        self.manager.transition.direction = 'right'
        self.manager.current = 'menu'


sm = ScreenManager()

Logger.info('Preparation: Loading menu')
sm.add_widget(MenuScreen(name='menu'))

Logger.info('Preparation: Loading settings')
sm.add_widget(SettingsScreen(name='settings'))

Logger.info('Preparation: Loading getting passwords')
sm.add_widget(GetPassword(name='get_password'))

Logger.info('Preparation: Loading setting passwords')
sm.add_widget(SetPassword(name='set_password'))

Logger.info('Preparation: Loading deleting password')
sm.add_widget(DelPassword(name='del_password'))

Logger.info('Preparation: Loading info')
sm.add_widget(InfoScreen(name='info'))


class PyPassword(App, BoxLayout):
    Logger.info('Application: Building application')

    def build(self):
        return sm


if __name__ == '__main__':
    PyPassword().run()
