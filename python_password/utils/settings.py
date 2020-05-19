# -*- coding: utf-8 -*-
from json import dump, load

from python_password.utils.files import appdata, Files


default_settings = {
    'theme': 'Light'
}


def create_settings():
    try:
        open(appdata(Files.settings), 'x')
    except FileExistsError:
        pass
    with open(appdata(Files.settings), 'w') as f:
        dump(default_settings, f)


reset_settings = create_settings


def set_setting(name: str, value):
    try:
        open(appdata(Files.settings))
    except FileNotFoundError:
        create_settings()
    finally:
        with open(appdata(Files.settings)) as f:
            settings = load(f)

    settings[name] = value

    with open(appdata(Files.settings), 'w') as f:
        dump(settings, f)


def get_setting(name: str):
    try:
        open(appdata(Files.settings))
    except FileNotFoundError:
        create_settings()
    finally:
        with open(appdata(Files.settings)) as f:
            settings = load(f)
    try:
        result = settings[name]
    except IndexError:
        return IndexError('Missing setting')
    else:
        return result


def set_theme(theme: str):
    set_setting('theme', theme)


def get_theme():
    return get_setting('theme')
