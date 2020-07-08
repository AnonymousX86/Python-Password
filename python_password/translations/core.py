# -*- coding: utf-8 -*-
from json import load, dump
from os import sep, mkdir
from pathlib import Path

from requests import get

from utils.files import appdata
from utils.settings import set_setting


default_messages = {
    "__info__": {
        "language": "en",
        "compatible_version": "0.2.5",
    },
    "alpha": "alfa",
    "beta": "beta",
    "passwords": "Passwords",
    "settings": "Settings",
    "info": "Info",
    "language": "Language",
    "switch_theme": "Switch theme",
    "password_alias": "Password alias",
    "password_value": "Password value",
    "x_characters_long": "{0}+ characters long.",
    "save_password": "Save password",
    "remove_password": "Remove password",
    "password_count_0": "There are no passwords in database.",
    "passwords_count_1": "There's only 1 password in database.",
    "passwords_count_x": "There are {0} passwords in database.",
    "refresh": "Refresh",
    "change_master": "Change {0} password",
    "new_master": "New {0} password",
    "save": "Save",
    "reset": "Reset",
    "export_backup": "Export backup",
    "import_backup": "Import backup",
    "about": "About the program",
    "name": "Name",
    "version": "Version",
    "author": "Author",
    "icon": "Program icon",
    "3rd_party": "3rd party software",
    "links": "Useful links",
    "github": "GitHub repository",
    "faq": "FAQ",
    "mail": "Mail",
    "available_languages": "Available languages",
    "add_language": "Add language",
    "warning": "Warning!",
    "whoops": "Whoops!",
    "success": "Success!",
    "ok": "OK",
    "yes": "Yes",
    "no": "No",
    "wip_title": "Work in progress",
    "wip_text": "This feature is under development.",
    "ctx_text": "Choose what do you want to do wth this password.",
    "copy": "Copy",
    "delete": "Delete",
    "nothing": "Nothing",
    "success_save": "Password \"{0}\" successfully saved.",
    "success_copy": "Password copied to clipboard. Now you can paste in somewhere.",
    "success_delete": "Password \"{0}\" successfully deleted.",
    "success_new_master": "New {0} passwords successfully saved.",
    "confirm_delete": "Do you really want to delete \"{0}\" password?",
    "confirm_randomize_alpha": "This will randomize alpha password. It will be super safe, but you probably will not be"
                               " able to re-enter this password later. You will not be able to access already saved"
                               " passwords. Do you want to continue?",
    "confirm_randomize_beta": "This will randomize beta password. It will be super safe, but you probably will not be"
                              " able to re-enter this password later. Do you want to continue?",
    "error_bad_format": "An critical error has occurred. Passwords are saved to local database in wrong way.",
    "error_invalid_token": "Alpha password do not match. If you want to access this password, please change alpha"
                           " password. If needed, change beta password too.",
    "error_no_alias": "Please provide password alias at first",
    "error_alias_too_short": "Password alias has to be at least {0} characters long",
    "error_already_exists": "That password already exists in database.",
    "error_not_exists": "That password do not exists in database.",
    "error_missing_master_title": "Missing {0} password",
    "error_missing_master_text": "It's needed for safe password storing. Do you want to provide it by yourself, or let"
                                 " program to randomize it?",
    "error_master_too_short": "{0} password should be at least {1} characters long.",
    "error_input_too_short": "At least one value is too short.",
    "error_input_invalid": "At last one value is invalid.",
    "error_locale_missing": "This language is not found, do you want to download it?",
    "error_unknown": "An error has occurred: {0}",
    "set_password": "Set password",
    "randomize": "Randomize",
    "tip_1_title": "Welcome to {0}",
    "tip_1_text_1": "Save your first password, by entering",
    "tip_1_text_2": "it's data on the right.",
    "tip_2_title": "Congratulations!",
    "tip_2_text_1": "You have saved your's 1st password.",
    "tip_2_text_2": "Preview it just by clicking it.",
    "restart_required": "To save changes, please restart app.",
    "login": "Login",
    "password": "Password",
    "log_in": "Log in"
}
default_language = default_messages['__info__']['language']
compatible_version = default_messages['__info__']['compatible_version']


def get_messages(lang: str):
    try:
        # Try load preferred language
        open(json_appdata(lang))
    except FileNotFoundError:
        set_locale(default_language)
        try:
            # Try load default language
            open(json_appdata(default_language))
        except FileNotFoundError:
            # Load messages from Python scope
            messages = default_messages
            save_default_messages()
        else:
            # Load default language
            with open(json_appdata(default_language), encoding='utf-8') as f:
                messages = load(f)
    else:
        # Load preferred language
        with open(json_appdata(lang), encoding='utf-8') as f:
            messages = load(f)
    return messages


def check_language(name: str):
    try:
        open(json_appdata(name))
    except FileNotFoundError:
        return False
    else:
        return True


def save_default_messages():
    try:
        open(json_appdata(default_language))
    except FileNotFoundError:
        create_locales_directory()
        open(json_appdata(default_language), 'x')
    with open(json_appdata(default_language), 'w') as f:
        dump(default_messages, f)


def download_locale(name: str):
    create_locales_directory()
    source = f'https://raw.githubusercontent.com/AnonymousX86/Python-Password/master/' \
             f'python_password/translations/locales/{name}.json'
    locale = get(source)
    with open(json_appdata(name), 'wb') as f:
        f.write(locale.content)


def json_appdata(lang: str):
    return appdata(f'locales{sep}{lang}.json')


def _json_locales(lang: str):
    return f'{Path().absolute()}{sep}locales{sep}{lang}.json'


def create_locales_directory():
    try:
        mkdir(appdata('locales'))
    except FileExistsError:
        pass


def set_locale(lang: str):
    set_setting('language', lang)


def test_locales(lang_list=None):
    if lang_list is None:
        lang_list = ['en', 'pl']
    for lang in lang_list:
        with open(_json_locales(lang), encoding='utf-8') as f:
            json_data = load(f)
        assert len(default_messages)-1 == len(json_data), f'Not all keys are included in "{lang.upper()}.JSON"'
        for key in default_messages.keys():
            if key != '__info__':
                try:
                    default_value = default_messages[key]
                except KeyError:
                    default_value = None
                assert default_value is not None, f'Key "{key}" not found in default values'
                try:
                    json_value = json_data[key]
                except KeyError:
                    json_value = None
                assert json_value is not None, f'Key "{key}" not found in "{lang.upper()}.JSON" values'
