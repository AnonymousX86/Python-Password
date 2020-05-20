# -*- coding: utf-8 -*-
from json import dump, load

from python_password.utils.files import appdata, Files


default_settings = {
    'theme': 'Light',
    'text_color_hex': '111111',
    'text_color_rgba': [.06, .06, .06, 1],
    'language': 'en'
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


def get_setting(name: str, second_try=False):
    try:
        open(appdata(Files.settings))
    except FileNotFoundError:
        create_settings()
    finally:
        with open(appdata(Files.settings)) as f:
            settings = load(f)
    try:
        result = settings[name]
    except KeyError:
        if not second_try:
            reset_settings()
            return get_setting(name, second_try=True)
        else:
            return KeyError('Missing setting')
    else:
        return result


def set_theme(theme: str):
    set_setting('theme', theme)
    if theme == 'Dark':
        set_setting('text_color_hex', 'ffffff')
        set_setting('text_color_rgba', [1, 1, 1, 1])
    elif theme == 'Light':
        set_setting('text_color_hex', '111111')
        set_setting('text_color_rgba', [.06, .06, .06, 1])
    else:
        raise NameError('No theme found')


def get_theme():
    return get_setting('theme')
