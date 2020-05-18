# -*- coding: utf-8 -*-
from os import getenv, path, sep, mkdir


class Files:
    """Names for program's files."""
    alpha_key = 'Alpha.key'
    beta_key = 'Beta.key'
    sqlite = 'Passwords.db'


def generate_appdata():
    """Creates ``PyPassword`` ~/AppData/Local/PyPassword directory if not exists."""
    try:
        mkdir(f'{getenv("LOCALAPPDATA")}{sep}PyPassword')
    except FileExistsError:
        pass


def appdata(filename: str):
    """Linking to user data in ~/AppData/Local/PyPassword."""
    generate_appdata()
    return path.join(
        path.dirname(__file__),
        f'{getenv("LOCALAPPDATA")}{sep}PyPassword{sep}{filename}'
    )


def create_in_appdata(file_name: str):
    try:
        open(appdata(file_name), 'x')
    except FileExistsError:
        pass


def check_alpha():
    try:
        open(appdata(Files.alpha_key))
    except FileNotFoundError:
        return False
    else:
        return True


def check_beta():
    try:
        open(appdata(Files.beta_key))
    except FileNotFoundError:
        return False
    else:
        return True
