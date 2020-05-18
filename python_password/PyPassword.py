# -*- coding: utf-8 -*-
"""Simple password manager app."""
from os import urandom
from webbrowser import open_new_tab

from cryptography.fernet import InvalidToken
from kivy import Config, require as kivy_require
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton, MDRaisedButton, MDFillRoundFlatIconButton, \
    MDRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, ThreeLineIconListItem
from pyperclip import copy

from python_password.utils.crypto import *
from python_password.utils.database import *
from python_password.utils.files import *


class SimpleDialog:
    """Simple dialogs."""

    def __init__(self, title, text, alert_text='OK', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.text = text
        self.alert_text = alert_text
        self.auto_dismiss = False

    def alert(self):
        """Dialog with only ``OK`` button."""
        alert = MDDialog(
            title=self.title,
            text=self.text,
            auto_dismiss=self.auto_dismiss,
            buttons=[
                MDRaisedButton(
                    text=self.alert_text,
                    on_release=lambda x: alert.dismiss()
                )
            ]
        )
        return alert


class NewbieTip(ThreeLineIconListItem):
    """Widget that's showed when there's one or two passwords in database."""
    icon = StringProperty()


class ContentNavigationDrawer(BoxLayout):
    """Container for side menu."""
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

    def change_screen(self, name):
        self.nav_drawer.set_state('close')
        self.screen_manager.current = name


class PyPassword(MDApp):
    """Main application wrapper."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = 'Indigo'
        self.theme_cls.theme_style = 'Dark'
        self.text_color_hex = 'ffffff'
        self.passwords = []
        self.info = {
            'name': 'Python Password',
            'version': '0.2.3',
            'author': 'Jakub Suchenek',
            'github': 'https://github.com/AnonymousX86/Python-Password',
            'faq': 'https://github.com/AnonymousX86/Python-Password/blob/master/docs/FAQ.md',
            'mail': 'mailto:jakub.suchenek.25@gmail.com',
            'icon': 'Icon made by Freepik from www.flaticon.com',
            'rd_party': 'UPX, Kivy and KivyMD'
        }

    # It has to be outside ``__init__``
    text_color_hsl = ListProperty([1, 1, 1, 1])

    def build(self):
        with open(f'kv_templates{sep}PyPassword.kv', encoding='utf8') as fd:
            kv = Builder.load_string(fd.read())
        return kv

    def on_start(self):
        self.update_passwords_list()
        self.masters_ok()
        # self.switch_theme()

    # ================================
    #           Information
    # ================================

    def ctx_password(self, instance):
        """Shows dialog with options what to do with password."""
        ctx_dialog = MDDialog(
            title=f'[color=#{self.text_color_hex}]{instance.text.capitalize()}[/color]',
            text='Choose what do you want to do wth this password.',
            auto_dismiss=False,
            buttons=[
                MDRectangleFlatIconButton(
                    icon='content-copy',
                    text='Copy',
                    on_release=lambda x: [
                        self.copy_password(instance.text),
                        ctx_dialog.dismiss()
                    ]
                ),
                MDRectangleFlatIconButton(
                    icon='trash-can-outline',
                    text='Delete',
                    on_release=lambda x: [
                        self.del_password(instance.text),
                        ctx_dialog.dismiss()
                    ]
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
        info_dialog = MDDialog(
            title=f'[color={self.text_color_hex}]' +
                  (name.capitalize() if name != 'rd_party' else '3rd party software') + '[/color]',
            text=self.info[name],
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text='OK', on_release=lambda x: info_dialog.dismiss()),
                MDRectangleFlatIconButton(
                    text='Freepik', icon='web',
                    on_release=lambda x:
                    self.open_url('https://www.freepik.com/')
                ) if name == 'icon' else None
                ]
        )
        info_dialog.open()

    def wip_info(self):
        info_dialog = SimpleDialog(
            title='Work in progress',
            text='This feature is under development.'
        ).alert()
        info_dialog.open()

    # ================================
    #        Passwords managing
    # ================================

    def add_password(self):
        alias_box = self.root.ids.password_alias
        value_box = self.root.ids.password_value
        if self.masters_ok():
            ok_alias = self.validate_input(alias_box, 3)
            ok_value = self.validate_input(value_box, 6)
            if not (ok_alias and ok_value):
                result_dialog = SimpleDialog(
                    title='Whoops!',
                    text='The entered values are too short or invalid.'
                ).alert()
            else:
                password_alias = alias_box.text.capitalize()
                password_value = value_box.text
                if already_exists(password_alias):
                    result_dialog = SimpleDialog(
                        title='Whoops!',
                        text='That password already exists or not all settings are set.'
                    ).alert()
                else:
                    save_password(
                        password_alias,
                        encrypt(password_value)
                    )
                    result_dialog = SimpleDialog(
                        title='Success!',
                        text=f'Password "{password_alias}" successfully saved.'
                    ).alert()
            result_dialog.open()
        alias_box.text = ''
        value_box.text = ''
        self.update_passwords_list()

    def copy_password(self, password=None):
        to_decrypt = get_one_password(password)
        if to_decrypt is None:
            result_dialog = SimpleDialog(
                title='Warning!',
                text='That password do not exists in database.'
            ).alert()
        elif type(to_decrypt) is not bytes:
            result_dialog = SimpleDialog(
                title='Warning!',
                text='An critical error has occurred. Passwords are saved to local database in wrong way.'
            ).alert()
        else:
            decrypted = decrypt(to_decrypt)
            if type(decrypted) is InvalidToken:
                result_dialog = SimpleDialog(
                    title='Warning!',
                    text='Alpha password do not match. If you want to access this password,'
                         ' please change alpha password. If needed, change beta password too.'
                ).alert()
            elif type(decrypted) is not str:
                result_dialog = SimpleDialog(
                    title='Warning!',
                    text=f'An error has occurred: {decrypted}'
                ).alert()
            else:
                copy(decrypted)
                result_dialog = SimpleDialog(
                    title='Success!',
                    text='Password copied to clipboard. Now you can paste in somewhere.'
                ).alert()
        result_dialog.open()
        self.update_passwords_list()

    def del_password(self, password=None):
        if password is None:
            password = self.root.ids.del_password_alias.text.capitalize()
        self.root.ids.del_password_alias.text = ''
        if len(password) == 0:
            result_dialog = SimpleDialog(
                title='Whoops!',
                text='Please provide password alias at first.'
            ).alert()
        elif len(password) < 3:
            result_dialog = SimpleDialog(
                title='Whoops!',
                text='Password alias has to be at least 3 characters long.'
            ).alert()
        else:
            to_del = get_one_password(password)
            if to_del is None:
                result_dialog = SimpleDialog(
                    title='Warning!',
                    text='That password do not exists in database'
                ).alert()
            elif type(to_del) is not bytes:
                result_dialog = SimpleDialog(
                    title='Warning!',
                    text='An critical error has occurred. Passwords are saved to local database in wrong way.'
                ).alert()
            else:
                result_dialog = MDDialog(
                    title='Attention',
                    text=f'Do you really want to delete "{password}" password?',
                    auto_dismiss=False,
                    buttons=[
                        MDFillRoundFlatIconButton(
                            text='Yes',
                            icon='check-circle-outline',
                            on_release=lambda x: [
                                self._del_password_confirm(password),
                                result_dialog.dismiss()
                            ]
                        ),
                        MDRoundFlatIconButton(
                            text='No',
                            icon='close-circle-outline',
                            on_release=lambda x: self.dismiss_and_back(result_dialog)
                        )
                    ]
                )
        result_dialog.open()

    def _del_password_confirm(self, password):
        del_password(password)
        result_dialog = SimpleDialog(
            title='Success!',
            text=f'Password "{password}" successfully deleted.'
        ).alert()
        result_dialog.open()
        self.update_passwords_list()

    # ================================
    #      Alpha & beta passwords
    # ================================

    def masters_ok(self):
        """Checks if master passwords are OK."""
        if not check_beta():
            alert_dialog = MDDialog(
                title='Missing beta password',
                text='I\'ve noticed, that you have not set beta password. It\'s needed for safe password storing.'
                     ' Do you want to provide it by yourself, or let program to randomize it?',
                auto_dismiss=False,
                buttons=[
                    MDFillRoundFlatIconButton(
                        text='Set password',
                        icon='account-key-outline',
                        on_release=lambda x: self.dismiss_and_back(alert_dialog, 'settings')
                    ),
                    MDRoundFlatIconButton(
                        text='Randomize',
                        icon='dice-multiple-outline',
                        on_release=lambda x: [
                            self.reset_beta(),
                            alert_dialog.dismiss()
                        ]
                    )
                ]
            )
            alert_dialog.open()
            return False
        elif not check_alpha():
            alert_dialog = MDDialog(
                title='Missing alpha password',
                text='I\'ve noticed, that you have not set alpha password. It\'s needed for safe password storing.'
                     ' Do you want to provide it by yourself, or let program to randomize it?',
                auto_dismiss=False,
                buttons=[
                    MDFillRoundFlatIconButton(
                        text='Set password',
                        icon='account-key-outline',
                        on_release=lambda x: self.dismiss_and_back(alert_dialog, 'settings')
                    ),
                    MDRoundFlatIconButton(
                        text='Randomize',
                        icon='dice-multiple-outline',
                        on_release=lambda x: [
                            self.reset_alpha(),
                            alert_dialog.dismiss()
                        ]
                    )
                ]
            )
            alert_dialog.open()
            return False
        else:
            return True

    def change_master(self, which: str, preset=None):
        which = which.lower()
        if which == 'alpha':
            password_box = self.root.ids.alpha_change
            generate_func = generate_alpha
        elif which == 'beta':
            password_box = self.root.ids.beta_change
            generate_func = generate_beta
        else:
            raise NameError(f'{which.capitalize()} password do not exists')

        password = password_box.text.encode('utf-8') if preset is None else preset

        if len(password) < 6:
            password_box.error = True
            result_dialog = SimpleDialog(
                title='Whoops!',
                text=f'{which.capitalize()} password should be at least 6 characters long.'
            ).alert()
        else:
            password_box.error = False
            generate_func(password)
            result_dialog = MDDialog(
                title='Success!',
                text=f'New {which} password successfully saved.',
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text='OK',
                        on_release=lambda x: self.dismiss_and_back(result_dialog)
                    )
                ]
            )

        password_box.text = ''
        result_dialog.open()

    def reset_alpha(self):
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
                        self.change_master('alpha', urandom(16)),
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

    def reset_beta(self):
        confirm_dialog = MDDialog(
            title='Warning!',
            text='This will randomize beta password. It will be super safe, but you probably will not be able to'
                 ' re-enter this password later. Do you want to continue?',
            auto_dismiss=False,
            buttons=[
                MDFillRoundFlatIconButton(
                    icon='check-circle-outline',
                    text='Yes',
                    on_release=lambda x: [
                        self.change_master('beta', urandom(16)),
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
        self.wip_info()
        # TODO - Making a backup

    def backup_import(self):
        self.wip_info()
        # TODO - importing a backup

    # ================================
    #            Passwords
    # ================================

    def _fetch_passwords(self):
        q = gel_all_passwords()
        passwords = [p[0] for p in q] if q is not None else []
        self.passwords = passwords

    def _set_passwords_list(self):
        self.root.ids.passwords_list.clear_widgets()
        for password in sorted(self.passwords):
            self.root.ids.passwords_list.add_widget(
                OneLineListItem(
                    text=password,
                    on_release=lambda x: self.ctx_password(x)
                )
            )

    def _set_passwords_count(self):
        count = len(self.passwords)
        if count == 0:
            text = 'There are no passwords in database.'
            self.root.ids.passwords_list.add_widget(
                NewbieTip(
                    text='Welcome to Python Password',
                    secondary_text='Save your first password, by entering',
                    tertiary_text='it\'s data on the right',
                    icon='arrow-right-bold-circle'
                )
            )
        elif count == 1:
            text = 'There\'s only 1 password in database.'
            self.root.ids.passwords_list.add_widget(
                NewbieTip(
                    text='Congratulations!',
                    secondary_text='You have saved your\'s 1st password.',
                    tertiary_text='Preview it just by clicking it.',
                    icon='arrow-up-bold-circle'
                )
            )
        else:
            text = f'There are {count} passwords in database.'
        self.root.ids.passwords_count.text = text

    def update_passwords_list(self):
        self._fetch_passwords()
        self._set_passwords_list()
        self._set_passwords_count()

    # ================================
    #               Misc
    # ================================

    def switch_theme(self, force=None):
        if force is not None:
            self.theme_cls.theme_style = force

        elif self.theme_cls.theme_style == 'Light':
            self.theme_cls.theme_style = 'Dark'
            self.text_color_hex = 'ffffff'
            self.text_color_hsl = (1, 1, 1, 1)

        elif self.theme_cls.theme_style == 'Dark':
            self.theme_cls.theme_style = 'Light'
            self.text_color_hex = '111111'
            self.text_color_hsl = (.06, .06, .06, 1)

        else:
            raise NameError('No theme found')

    def open_url(self, url):
        open_new_tab(url)

    def dismiss_and_back(self, instance, where='passwords'):
        self.root.ids.screen_manager.current = where
        instance.dismiss()

    def validate_input(self, instance, length):
        """
        Checks text input.
        :param instance: Which widget has to be checked.
        :param length: Minimum length of provided text.
        """
        instance.error = True if len(instance.text) < length else False
        return not instance.error


if __name__ == '__main__':
    kivy_require('1.11.1')

    Config.set('kivy', 'desktop', 1)
    Config.set('kivy', 'exit_on_esc', 0)
    Config.set('kivy', 'pause_on_minimize', 0)
    Config.set('graphics', 'resizable', 1)

    Config.set('kivy', 'log_dir', appdata(f'.{sep}logs{sep}'))
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_level', 'warning')
    Config.set('kivy', 'log_maxfiles', 10)

    Config.write()

    PyPassword().run()
