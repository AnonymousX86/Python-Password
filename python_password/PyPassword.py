# -*- coding: utf-8 -*-
"""Simple password manager app."""
from os import urandom
from re import match
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

from python_password.exceptions.validation import *
from python_password.utils.crypto import *
from python_password.utils.database import *
from python_password.utils.files import *
from python_password.utils.settings import *
from translations.core import *


class SimpleDialog:
    """Simple dialogs."""

    def __init__(self, title, text, alert_text, **kwargs):
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
        self.theme_cls.theme_style = 'Light'
        self.text_color_hex = get_setting('text_color_hex')
        self.passwords = []
        self.info = {
            'name': 'Python Password',
            'version': '0.2.5',
            'author': 'Jakub Suchenek',
            'github': 'https://github.com/AnonymousX86/Python-Password',
            'faq': 'https://github.com/AnonymousX86/Python-Password/blob/master/docs/FAQ.md',
            'mail': 'mailto:jakub.suchenek.25@gmail.com',
            'icon': 'Icon made by Freepik from www.flaticon.com',
            '3rd_party': 'UPX, Kivy and KivyMD'
        }
        self.all_languages = {
            'en': 'English',
            'pl': 'Polski'
        }
        self.current_language = get_setting('language')
        self.messages = {}

    # It has to be outside ``__init__``
    text_color_rgba = ListProperty(get_setting('text_color_rgba'))

    def build(self):
        self.update_messages()
        with open(f'kv_templates{sep}PyPassword.kv', encoding='utf8') as fd:
            kv = Builder.load_string(fd.read())
        return kv

    def on_start(self):
        self.update_passwords_list()
        self.masters_ok()
        self.switch_theme(get_theme())
        self.update_languages_list()

    # ================================
    #           Information
    # ================================

    def ctx_password(self, instance):
        """Shows dialog with options what to do with password."""
        ctx_dialog = MDDialog(
            title=f'[color=#{self.text_color_hex}]{instance.text.capitalize()}[/color]',
            text=self.tr('ctx_text'),
            auto_dismiss=False,
            buttons=[
                MDRectangleFlatIconButton(
                    icon='content-copy',
                    text=self.tr('copy'),
                    on_release=lambda x: [
                        self.copy_password(instance.text),
                        ctx_dialog.dismiss()
                    ]
                ),
                MDRectangleFlatIconButton(
                    icon='trash-can-outline',
                    text=self.tr('delete'),
                    on_release=lambda x: [
                        self.del_password(instance.text, True),
                        ctx_dialog.dismiss()
                    ]
                ),
                MDRectangleFlatIconButton(
                    icon='arrow-left-circle-outline',
                    text=self.tr('nothing'),
                    on_release=lambda x: ctx_dialog.dismiss()
                )
            ]
        )
        ctx_dialog.open()

    def detailed_info(self, name: str):
        """Opens dialog about specific info about program in ``info`` screen."""
        info_dialog = MDDialog(
            title=self.tr(name, is_title=True),
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
            title=self.tr('wip_title'),
            text=self.tr('wip_text'),
            alert_text=self.tr('ok')
        ).alert()
        info_dialog.open()

    # ================================
    #        Passwords managing
    # ================================

    # TODO - Alfa password should be entered before copying or removing password.

    def add_password(self):
        alias_box = self.root.ids.password_alias
        value_box = self.root.ids.password_value
        if self.masters_ok():
            ok_alias = self.validate_input(alias_box, 3)
            ok_value = self.validate_input(value_box, 6)
            if ok_alias is ValueTooShort or ok_value is ValueTooShort:
                result_dialog = SimpleDialog(
                    title=self.tr('whoops'),
                    text=self.tr('error_input_too_short'),
                    alert_text=self.tr('ok')
                ).alert()
            elif ok_alias is PatternError or ok_value is PatternError:
                result_dialog = SimpleDialog(
                    title=self.tr('whoops'),
                    text=self.tr('error_input_invalid'),
                    alert_text=self.tr('ok')
                ).alert()
            else:
                password_alias = alias_box.text.capitalize()
                password_value = value_box.text
                if already_exists(password_alias):
                    result_dialog = SimpleDialog(
                        title=self.tr('whoops'),
                        text=self.tr('error_already_exists'),
                        alert_text=self.tr('ok')
                    ).alert()
                else:
                    save_password(
                        password_alias,
                        encrypt(password_value)
                    )
                    result_dialog = SimpleDialog(
                        title=self.tr('success'),
                        text=self.tr('success_save', txt_format=password_alias),
                        alert_text=self.tr('ok')
                    ).alert()
            result_dialog.open()
        alias_box.text = ''
        value_box.text = ''
        self.update_passwords_list()

    def copy_password(self, password=None):
        to_decrypt = get_one_password(password)
        if to_decrypt is None:
            result_dialog = SimpleDialog(
                title=self.tr('warning'),
                text=self.tr('error_not_exists'),
                alert_text=self.tr('ok')
            ).alert()
        elif type(to_decrypt) is not bytes:
            result_dialog = SimpleDialog(
                title=self.tr('warning'),
                text=self.tr('error_bad_format'),
                alert_text=self.tr('ok')
            ).alert()
        else:
            decrypted = decrypt(to_decrypt)
            if type(decrypted) is InvalidToken:
                result_dialog = SimpleDialog(
                    title=self.tr('warning'),
                    text=self.tr('error_invalid_token'),
                    alert_text=self.tr('ok')
                ).alert()
            elif type(decrypted) is not str:
                result_dialog = SimpleDialog(
                    title=self.tr('warning'),
                    text=self.tr('error_unknown', txt_format=decrypted),
                    alert_text=self.tr('ok')
                ).alert()
            else:
                copy(decrypted)
                result_dialog = SimpleDialog(
                    title=self.tr('success'),
                    text=self.tr('success_copy'),
                    alert_text=self.tr('ok')
                ).alert()
        result_dialog.open()
        self.update_passwords_list()

    def del_password(self, password=None, force=False):
        if password is None:
            password = self.root.ids.del_password_alias.text.capitalize()
        self.root.ids.del_password_alias.text = ''
        if not force and len(password) == 0:
            result_dialog = SimpleDialog(
                title=self.tr('whoops'),
                text=self.tr('error_no_alias'),
                alert_text=self.tr('ok')
            ).alert()
        elif not force and len(password) < 3:
            result_dialog = SimpleDialog(
                title=self.tr('whoops'),
                text=self.tr('error_alias_too_short', txt_format='3'),
                alert_text=self.tr('ok')
            ).alert()
        else:
            to_del = get_one_password(password)
            if to_del is None:
                result_dialog = SimpleDialog(
                    title=self.tr('warning'),
                    text=self.tr('error_not_exists'),
                    alert_text=self.tr('ok')
                ).alert()
            elif type(to_del) is not bytes:
                result_dialog = SimpleDialog(
                    title=self.tr('warning'),
                    text=self.tr('error_bad_format'),
                    alert_text=self.tr('ok')
                ).alert()
            else:
                result_dialog = MDDialog(
                    title=self.tr('warning'),
                    text=self.tr('confirm_delete', txt_format=password),
                    auto_dismiss=False,
                    buttons=[
                        MDFillRoundFlatIconButton(
                            text=self.tr('yes'),
                            icon='check-circle-outline',
                            on_release=lambda x: [
                                self._del_password_confirm(password),
                                result_dialog.dismiss()
                            ]
                        ),
                        MDRoundFlatIconButton(
                            text=self.tr('no'),
                            icon='close-circle-outline',
                            on_release=lambda x: self.dismiss_and_back(result_dialog)
                        )
                    ]
                )
        result_dialog.open()

    def _del_password_confirm(self, password: str):
        del_password(password)
        result_dialog = SimpleDialog(
            title=self.tr('success'),
            text=self.tr('success_delete', txt_format=password),
            alert_text=self.tr('ok')
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
                title=self.tr('error_missing_master_title', txt_format=self.tr('beta')),
                text=self.tr('error_missing_master_text'),
                auto_dismiss=False,
                buttons=[
                    MDFillRoundFlatIconButton(
                        text=self.tr('set_password'),
                        icon='account-key-outline',
                        on_release=lambda x: self.dismiss_and_back(alert_dialog, 'settings')
                    ),
                    MDRoundFlatIconButton(
                        text=self.tr('randomize'),
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
                title=self.tr('error_missing_master_title', txt_format=self.tr('alpha')),
                text=self.tr('error_missing_master_text'),
                auto_dismiss=False,
                buttons=[
                    MDFillRoundFlatIconButton(
                        text=self.tr('set_password'),
                        icon='account-key-outline',
                        on_release=lambda x: self.dismiss_and_back(alert_dialog, 'settings')
                    ),
                    MDRoundFlatIconButton(
                        text=self.tr('randomize'),
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

    # TODO - Alfa password should be entered before changing master password.

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
                title=self.tr('whoops'),
                text=self.tr('error_master_too_short', txt_format=[self.tr(which), '6']),
                alert_text=self.tr('ok')
            ).alert()
        else:
            password_box.error = False
            generate_func(password)
            result_dialog = MDDialog(
                title=self.tr('success'),
                text=self.tr('success_new_master', txt_format=self.tr(which)),
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text=self.tr('ok'),
                        on_release=lambda x: self.dismiss_and_back(result_dialog)
                    )
                ]
            )

        password_box.text = ''
        result_dialog.open()

    def reset_alpha(self):
        confirm_dialog = MDDialog(
            title=self.tr('warning'),
            text=self.tr('confirm_randomize_alpha'),
            auto_dismiss=False,
            buttons=[
                MDFillRoundFlatIconButton(
                    text=self.tr('yes'),
                    icon='check-circle-outline',
                    on_release=lambda x: [
                        self.change_master('alpha', urandom(16)),
                        confirm_dialog.dismiss()
                    ]
                ),
                MDRoundFlatIconButton(
                    text=self.tr('no'),
                    icon='close-circle-outline',
                    on_release=lambda x: confirm_dialog.dismiss()
                )
            ]
        )
        confirm_dialog.open()

    def reset_beta(self):
        confirm_dialog = MDDialog(
            title=self.tr('warning'),
            text=self.tr('confirm_randomize_beta'),
            auto_dismiss=False,
            buttons=[
                MDFillRoundFlatIconButton(
                    text=self.tr('yes'),
                    icon='check-circle-outline',
                    on_release=lambda x: [
                        self.change_master('beta', urandom(16)),
                        confirm_dialog.dismiss()
                    ]
                ),
                MDRoundFlatIconButton(
                    text=self.tr('no'),
                    icon='close-circle-outline',
                    on_release=lambda x: confirm_dialog.dismiss()
                )
            ]
        )
        confirm_dialog.open()

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
            text = self.tr('password_count_0')
            self.root.ids.passwords_list.add_widget(
                NewbieTip(
                    text=self.tr('tip_1_title', txt_format=self.info['name']),
                    secondary_text=self.tr('tip_1_text_1'),
                    tertiary_text=self.tr('tip_1_text_2'),
                    icon='arrow-right-bold-circle'
                )
            )
        elif count == 1:
            text = self.tr('password_count_1')
            self.root.ids.passwords_list.add_widget(
                NewbieTip(
                    text=self.tr('tip_2_title'),
                    secondary_text=self.tr('tip_2_text_1'),
                    tertiary_text=self.tr('tip_2_text_2'),
                    icon='arrow-up-bold-circle'
                )
            )
        else:
            text = self.tr('passwords_count_x', txt_format=count)
        self.root.ids.passwords_count.text = text

    def update_passwords_list(self):
        self._fetch_passwords()
        self._set_passwords_list()
        self._set_passwords_count()

    # ================================
    #           Languages
    # ================================

    def _set_languages_list(self):
        self.root.ids.languages_list.clear_widgets()
        for lang in self.all_languages.keys():
            self.root.ids.languages_list.add_widget(
                OneLineListItem(
                    text=self.all_languages[lang],
                    on_release=lambda x: self.change_language(
                        list(self.all_languages.keys())[list(self.all_languages.values()).index(x.text)]
                    )
                )
            )

    def update_languages_list(self):
        self._set_languages_list()

    def update_messages(self):
        self.messages = get_messages(get_setting('language'))

    def change_language(self, lang: str):
        if not check_language(lang):
            result_dialog = MDDialog(
                title=self.tr('whoops'),
                text=self.tr('error_locale_missing'),
                auto_dismiss=False,
                buttons=[
                    MDRaisedButton(
                        text=self.tr('yes'),
                        on_release=lambda x: [
                            download_locale(lang),
                            set_locale(lang),
                            self.restart_required(),
                            result_dialog.dismiss()
                        ]
                    ),
                    MDRaisedButton(
                        text=self.tr('no'),
                        on_release=lambda x: result_dialog.dismiss()
                    )
                ]
            )
            result_dialog.open()
        else:
            set_locale(lang)
            self.restart_required()

    def add_language(self):
        self.open_url(
            'https://github.com/AnonymousX86/Python-Password/blob/master/docs/CONTRIBUTING.md#adding-new-locales'
        )

    def tr(self, text_id, txt_format=None, is_title=False):
        try:
            result = self.messages[text_id]
        except KeyError:
            try:
                result = default_messages[text_id]
            except KeyError:
                return f'Missing: {text_id}'
        if txt_format:
            result = result.format(txt_format)
        if is_title:
            result = f'[color=#{get_setting("text_color_hex")}]{result}[/color]'
        return result

    # ================================
    #               Misc
    # ================================

    def update_theme(self):
        self.text_color_hex = get_setting('text_color_hex')
        self.text_color_rgba = get_setting('text_color_rgba')
        self.theme_cls.theme_style = get_setting('theme')

    def switch_theme(self, force=None):
        """Changes theme to opposite or forced."""
        if force == 'Light':
            current = 'Dark'
        elif force == 'Dark':
            current = 'Light'
        else:
            current = self.theme_cls.theme_style

        if current == 'Light':
            self.theme_cls.theme_style = 'Dark'
            set_theme('Dark')
        elif current == 'Dark':
            self.theme_cls.theme_style = 'Light'
            set_theme('Light')
        else:
            raise NameError('No theme found')

        self.update_theme()

    def restart_required(self):
        result_dialog = SimpleDialog(
            title=self.tr('success'),
            text=self.tr('restart_required'),
            alert_text=self.tr('ok')
        ).alert()
        result_dialog.open()

    def open_url(self, url: str):
        """Opens URL in default browser."""
        open_new_tab(url)

    def dismiss_and_back(self, instance, where='passwords'):
        self.root.ids.screen_manager.current = where
        instance.dismiss()

    def validate_input(self, instance, length: int):
        if len(instance.text) < length:
            instance.error = True
            return ValueTooShort
        elif match(
                '^[A-Za-zĘÓĄŚŁŻŹĆŃęóąśłżźćń0-9][A-Za-z0-9ĘÓĄŚŁŻŹĆŃęóąśłżźćń &\\-_]+[A-Za-z0-9ĘÓĄŚŁŻŹĆŃęóąśłżźćń]$',
                instance.text
        ) is None:
            instance.error = True
            return PatternError
        else:
            instance.error = False
            return True


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
