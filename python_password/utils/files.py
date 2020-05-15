# -*- coding: utf-8 -*-
import os

from kivy import Logger


class Files:
    """Names for program's files."""
    alpha_key = 'Alpha.key'
    beta_key = 'Beta.key'
    sqlite = 'Passwords.db'


def file(filename: str, file_type='u'):
    """
    Add absolute path to file name.
    Linking to user data in ~/AppData/Local/PyPassword or
        program data directory next to ``.exe`` file.
    :param filename: File to access name.
    :param file_type: Is file program or user related.
    :return: Absolute path to file with specified name.
    """
    Logger.trace(f'Files: Accessing {filename} file ({file_type} type)')

    # Program files
    if file_type == 'p':
        return os.path.join(os.path.dirname(__file__), f'../PyPassword_data/{filename}')
    # User files
    elif file_type == 'u':
        return os.path.join(os.path.dirname(__file__), f'{os.getenv("LOCALAPPDATA")}/PyPassword/{filename}')
    else:
        Logger.critical(f'Files: Tried to access file of unknown type')
        raise NameError('That kind of files does not exist')


def generate_appdata():
    """Creates ``PyPassword`` folder in ~/AppData/Local."""
    Logger.trace('Structure: Trying to create ~\\AppData\\Local\\PyPassword directory')
    os.system('cd %localappdata% && md PyPassword')


def generate_salt(preset=None):
    """Generates salt - Beta.key file."""
    try:
        generate_appdata()
        open(file(Files.beta_key), 'x')
    except FileExistsError:
        pass
    else:
        Logger.info(f'Structure: {Files.beta_key} file not found, creating it.')
    finally:
        custom_salt = os.urandom(16) if preset is None else preset
        with open(file(Files.beta_key), 'wb') as f:
            f.write(custom_salt)
        Logger.info('Structure: Beta password changed.')
