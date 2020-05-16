# -*- coding: utf-8 -*-
import os

from kivy import Logger


class Files:
    """Names for program's files."""
    alpha_key = 'Alpha.key'
    beta_key = 'Beta.key'
    sqlite = 'Passwords.db'


def appdata(filename: str):
    """
    Linking to user data in ~/AppData/Local/PyPassword/.
    :param filename: File to access name.
    :return: Absolute path to file with specified name.
    """
    Logger.trace(f'Files: Accessing {filename} file')
    return os.path.join(os.path.dirname(__file__),
                        f'{os.getenv("LOCALAPPDATA")}{os.sep}PyPassword{os.sep}{filename}')


def generate_appdata():
    """Creates ``PyPassword`` folder in ~/AppData/Local."""
    Logger.trace('Structure: Trying to create ~\\AppData\\Local\\PyPassword directory')
    os.system('cd %localappdata% && md PyPassword')


def generate_salt(preset=None):
    """Generates salt - Beta.key file."""
    try:
        generate_appdata()
        open(appdata(Files.beta_key), 'x')
    except FileExistsError:
        pass
    else:
        Logger.info(f'Structure: {Files.beta_key} file not found, creating it.')
    finally:
        custom_salt = os.urandom(16) if preset is None else preset if type(preset) is bytes else preset.encode()
        with open(appdata(Files.beta_key), 'wb') as f:
            f.write(custom_salt)
        Logger.info('Structure: Beta password changed.')
