# -*- coding: utf-8 -*-
"""Simple password manager app."""
import base64
import webbrowser

import kivy
import pyperclip
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from kivy import Config
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton, MDRaisedButton, MDFillRoundFlatIconButton, \
    MDRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem

from python_password.utils.crypto import *
from python_password.utils.database import *
from python_password.utils.files import *


class Todo:
    """Methods to add to ``PyPassword`` - app wrapper."""

    # TODO - Add ``copy_password`` method
    def copy_password(self, alias):
        to_decrypt = query(
            'SELECT `password` FROM `passwords` WHERE `name` LIKE ?;',
            [alias]
        )
        n = type(to_decrypt)
        if n is not None:
            to_decrypt = to_decrypt[0][0]
            if n is bytes:
                with open(file(Files.alpha_key), 'rb') as f:
                    key = f.read()
                    f = Fernet(key)
                    try:
                        pyperclip.copy(str(f.decrypt(to_decrypt).decode('utf-8')))
                    except InvalidToken:
                        # Alpha key does not match
                        pass
                    else:
                        # Password copied to clipboard
                        pass
            else:
                # Bad password type, not saved to a ``byte``
                pass
        else:
            # That password does not exits
            pass

    # TODO - Add ``del_password`` method
    def del_password(self, alias):
        to_del = query(
            'SELECT `password` FROM `passwords` WHERE `name` LIKE ?;',
            [alias]
        )
        if to_del is not None:
            to_del = to_del[0][0]
            if type(to_del) is bytes:
                del_confirm = input('If you want to proceed, please once more enter password name: ')
                while True:
                    if alias == del_confirm:
                        try:
                            query(
                                'DELETE FROM `passwords` WHERE `name` LIKE ?;',
                                [alias]
                            )
                        except FileNotFoundError:
                            pass
                        else:
                            # Password deleted successfully
                            pass
                        finally:
                            break

                    elif del_confirm in ('c', 'cancel'):
                        # Action cancelled
                        break

                    else:
                        # Passwords do not match
                        del_confirm = input('Try once more: ')
            else:
                # Bad password type, that is a critical error
                pass
        else:
            # That password does not exists
            pass


class ContentNavigationDrawer(BoxLayout):
    """Container for side menu."""
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

    def change_screen(self, name):
        self.nav_drawer.set_state('close')
        self.screen_manager.current = name


# Kivy template for hor reload
KV = '''
#:import KivyLexer kivy.extras.highlight.KivyLexer
#:import HotReloadViewer kivymd.utils.hot_reload_viewer.HotReloadViewer


BoxLayout:

    CodeInput:
        lexer: KivyLexer()
        style_name: "native"
        on_text: app.update_kv_file(self.text)
        size_hint_x: .7

    HotReloadViewer:
        size_hint_x: .3
        path: app.path_to_kv_file
        errors: True
        errors_text_color: 1, 1, 0, 1
        errors_background_color: app.theme_cls.bg_dark
'''


class PyPassword(MDApp):
    """Main application wrapper."""
    Logger.info('Application: Building application')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.passwords = []
        raw = query('SELECT `name` FROM `passwords`;')
        if raw is not None:
            for password in raw:
                self.passwords.append(password[0])
        del raw

        self.info = {
            'name': 'Python Password',
            'version': '0.2.1',
            'author': 'Jakub Suchenek',
            'github': 'https://github.com/AnonymousX86/Python-Password',
            'faq': 'https://github.com/AnonymousX86/Python-Password/blob/master/docs/FAQ.md',
            'mail': 'mailto:jakub.suchenek.25@gmail.com',
            'icon': 'Icon made by Freepik from www.flaticon.com',
            'rd_party': 'UPX, Kivy and KivyMD'
        }

    def build(self):
        # Change main color
        self.theme_cls.primary_palette = 'Indigo'
        Logger.info(f'Application: Primary palette set to {self.theme_cls.primary_palette}')
        # Change theme (light/dark)
        self.theme_cls.theme_style = 'Light'
        Logger.info(f'Application: Theme style set to {self.theme_cls.theme_style}')

    def on_start(self):
        self.update_passwords()
        self.root.ids.screen_manager.current = 'settings'

    # ================================
    #    Context menus and dialogs
    # ================================

    def ctx_password(self, instance):
        """Shows dialog with options what to do with password."""
        Logger.trace('Called: ctx_password')
        ctx_dialog = MDDialog(
            title=instance.text.capitalize(),
            text='Choose what do you want to do wth this password.',
            auto_dismiss=False,
            buttons=[
                MDRectangleFlatIconButton(
                    icon='content-copy',
                    text='Copy',
                    on_release=lambda x: [self.wip_info(), ctx_dialog.dismiss()]
                ),
                MDRectangleFlatIconButton(
                    icon='trash-can-outline',
                    text='Delete',
                    on_release=lambda x: [self.wip_info(), ctx_dialog.dismiss()]
                ),
                MDRectangleFlatIconButton(
                    icon='arrow-left-circle-outline',
                    text='Nothing',
                    on_release=lambda x: ctx_dialog.dismiss()
                )
            ]
        )
        ctx_dialog.open()

    def detailed_info(self, name):
        """Opens dialog about specific info about program in ``info`` screen."""
        Logger.trace('Called: detailed_info')
        info_dialog = MDDialog(
            title=name.capitalize() if name != 'rd_party' else '3r party software',
            text=self.info[name],
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text='OK', on_release=lambda x: info_dialog.dismiss()),
                MDRectangleFlatIconButton(
                    text='Freepik', icon='web',
                    on_release=lambda x:
                    self.open_url('https://www.freepik.com/')
                ) if name == 'icon' else None,
            ]
        )
        info_dialog.open()

    def wip_info(self):
        Logger.trace('Called: wip_info')
        info_dialog = MDDialog(
            title='Warning',
            text='This feature is under development.',
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text='OK',
                    on_release=lambda x: info_dialog.dismiss()
                )
            ]
        )
        info_dialog.open()

    # ================================
    #        Passwords managing
    # ================================

    def add_password(self):
        """Adding passwords to database. Invoked by button in ``passwords`` menu."""
        Logger.trace('Called: add_password')
        alias_box = self.root.ids.password_alias
        value_box = self.root.ids.password_value

        self.validate_input(alias_box, 3)
        self.validate_input(value_box, 6)

        ok_alias = self.validate_input(alias_box, 3)
        ok_value = self.validate_input(value_box, 6)

        password_alias = alias_box.text
        password_value = value_box.text

        if ok_alias is True and ok_value is True:
            try:
                query(
                    'INSERT INTO passwords (`name`, `password`) VALUES (?, ?);',
                    [password_alias, encrypt(password_value)]
                )

            except sqlite3.IntegrityError:
                Logger.info(f'Passwords: Tried to save "{password_alias}" but already exists.')
                result_dialog = MDDialog(
                    title='Whoops!',
                    text='That password already exists.',
                    auto_dismiss=False,
                    buttons=[
                        MDRaisedButton(
                            text='OK',
                            on_press=lambda x: result_dialog.dismiss()
                        )
                    ]
                )

            else:
                Logger.info(f'Passwords: Password "{password_alias}" saved.')
                result_dialog = MDDialog(
                    title='Success!',
                    text=f'Password [b]{password_alias}[/b] successfully saved.',
                    auto_dismiss=False,
                    buttons=[
                        MDRaisedButton(
                            text='OK',
                            on_press=lambda x: result_dialog.dismiss()
                        )
                    ]
                )

        else:
            result_dialog = MDDialog(
                title='Whoops!',
                text='The entered data is invalid.',
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text='OK',
                        on_press=lambda x: result_dialog.dismiss()
                    )
                ]
            )

        result_dialog.open()

    def copy_password(self, password=None):
        """Copying password value to clipboard."""
        Logger.trace('Called: copy_password')
        pass

    def del_password(self, password=None):
        """
        Invoked by button in ``passwords`` screen,
            or ``Copy`` button in context menu from ``ctx_password`` method.
        """
        Logger.trace('Called: del_password')
        pass

    # ================================
    #          Alpha password
    # ================================

    def change_alpha(self, preset=None):
        """Changing alpha password based on text input or random value from ``reset_alpha`` method."""
        Logger.trace('Called: change_alpha')
        password_box = self.root.ids.alpha_change

        if preset is None:
            password = password_box.text
        else:
            password = preset

        if len(password) < 6:
            result_dialog = MDDialog(
                title='Whoops!',
                text='Password should be at least 6 characters long.',
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text='OK',
                        on_release=lambda x: result_dialog.dismiss()
                    )
                ]
            )
            password_box.error = True

        else:
            password_box.error = False
            try:
                open(file(Files.beta_key))
            except FileNotFoundError:
                generate_salt()
            finally:
                try:
                    open(file(Files.alpha_key))
                except FileNotFoundError:
                    open(file(Files.alpha_key), 'x')
                finally:
                    with open(file(Files.beta_key), 'rb') as f:
                        kdf = PBKDF2HMAC(
                            algorithm=hashes.SHA256(),
                            length=32,
                            salt=f.read(),
                            iterations=100000,
                            backend=default_backend()
                        )
                    with open(file(Files.alpha_key), 'wb') as f:
                        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
                        f.write(key)
                        Logger.info('Passwords: Alpha password has changed')

                    result_dialog = MDDialog(
                        title='Success!',
                        text='New alpha password successfully saved.',
                        auto_dismiss=False,
                        buttons=[
                            MDRaisedButton(
                                text='OK',
                                on_press=lambda x: self.dismiss_and_back(result_dialog)
                            )
                        ]
                    )

        password_box.text = ''
        result_dialog.open()

    def reset_alpha(self):
        """Changing alpha password to ``random_password`` function value."""
        Logger.trace('Called: reset_alpha')
        confirm_dialog = MDDialog(
            title='Warning!',
            text='This will randomize alpha password. It will be super safe, but you probably will not be able to'
                 ' re-enter this password later. You will not be able to copy already saved passwords.'
                 ' Do you want to continue?',
            auto_dismiss=False,
            buttons=[
                MDFillRoundFlatIconButton(
                    icon='check-circle-outline',
                    text='Yes',
                    on_release=lambda x: [
                        self.change_alpha(preset=rand_password()),
                        confirm_dialog.dismiss()
                    ]
                ),
                MDRoundFlatIconButton(
                    icon='close-circle-outline',
                    text='No',
                    on_release=lambda x: confirm_dialog.dismiss()
                )
            ]
        )
        confirm_dialog.open()

    # ================================
    #          Beta password
    # ================================

    def change_beta(self, preset=None):
        """Changes beta password, based on text input or random value from ``reset_beta`` method."""
        Logger.trace('Called: change_beta')
        password_box = self.root.ids.beta_change

        if preset is None:
            password = password_box.text
        else:
            password = preset

        if len(password) < 6:
            result_dialog = MDDialog(
                title='Whoops!',
                text='Password should be at least 6 characters long.',
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text='OK',
                        on_release=lambda x: result_dialog.dismiss()
                    )
                ]
            )
            password_box.error = True

        else:
            password_box.error = False
            generate_salt(preset=password)
            result_dialog = MDDialog(
                title='Success!',
                text='Password successfully saved.',
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text='OK',
                        on_release=lambda x: self.dismiss_and_back(result_dialog)
                    )
                ]
            )

        password_box.text = ''
        password_box.open()

    def reset_beta(self):
        """Changes beta password to random, 16 unicode characters long string."""
        Logger.trace('Called: reset_beta')
        confirm_dialog = MDDialog(
            title='Warning!',
            text='This will randomize beta password. It will be super safe, but you probably will not be able to'
                 ' re-enter this password later. Beta password is much more complex than alpha.'
                 ' Do you want to continue?',
            auto_dismiss=False,
            buttons=[
                MDFillRoundFlatIconButton(
                    icon='check-circle-outline',
                    text='Yes',
                    on_release=lambda x: [
                        self.change_beta(os.urandom(16)),
                        confirm_dialog.dismiss()
                    ]
                ),
                MDRoundFlatIconButton(
                    icon='close-circle-outline',
                    text='No',
                    on_release=lambda x: confirm_dialog.dismiss()
                )
            ]
        )
        confirm_dialog.open()

    # ================================
    #              Backup
    # ================================

    def backup_export(self):
        """Creates a backup of all passwords (including alpha and beta passwords)."""
        Logger.trace('Called: backup_export')
        self.wip_info()
        # TODO - Making a backup

    def backup_import(self):
        """Import passwords (including alpha and beta passwords)."""
        Logger.trace('Called: backup_import')
        self.wip_info()
        # TODO - importing a backup

    # ================================
    #               Misc
    # ================================

    def open_url(self, url):
        """Opens provided URL in default web browser."""
        Logger.trace('Called: open_url')
        webbrowser.open_new_tab(url)

    def dismiss_and_back(self, instance, where='passwords'):
        """
        Closes provided dialog and changes screen.
        :param instance: What dialog has to be closed.
        :param where: What screen has to be activated.
        """
        Logger.trace('Called: dismiss_and_back')
        self.root.ids.screen_manager.current = where
        instance.dismiss()

    def update_passwords(self):
        """Update passwords' list in main menu (``passwords`` screen)."""
        Logger.trace('Called: update_passwords')
        Logger.debug('Application: Passwords updating')

        # Remove all widgets
        self.root.ids.passwords_list.clear_widgets()

        # And create them updated
        for password in sorted(self.passwords):
            new_widget = OneLineListItem(
                text=password,
                on_release=lambda x: self.ctx_password(x)
            )
            self.root.ids.passwords_list.add_widget(new_widget)

        # Update passwords count
        count = len(self.passwords)
        if count == 0:
            text = 'There are no passwords in database.'
        elif count == 1:
            text = 'There\'s only 1 password in database.'
        else:
            text = f'There are {count} passwords in database.'

        self.root.ids.passwords_count.text = text

    def validate_input(self, instance, length):
        """
        Checks text input.
        :param instance: Which object has to be checked.
        :param length: Minimum length of provided text.
        """
        Logger.debug('Called: validate_input')

        if len(instance.text) < length:
            instance.error = True
        else:
            instance.error = False

        instance.canvas.ask_update()
        instance.parent.do_layout()

        return not instance.error


if __name__ == '__main__':
    kivy.require('1.11.1')

    Config.set('kivy', 'window_icon', file('icon.ico', 'p'))
    Config.set('kivy', 'desktop', 1)
    Config.set('kivy', 'exit_on_esc', 0)
    Config.set('kivy', 'pause_on_minimize', 0)
    Config.set('graphics', 'resizable', 1)

    Config.set('kivy', 'log_dir', file('./logs/', 'p'))
    Config.set('kivy', 'log_enable', 0)
    Config.set('kivy', 'log_level', 'warning')
    Config.set('kivy', 'log_maxfiles', 10)

    PyPassword().run()
