# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode
from random import choice
from string import ascii_letters, digits, punctuation

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from python_password.utils.files import appdata, Files, create_in_appdata


def _key():
    with open(appdata(Files.alpha_key), 'rb') as f:
        return Fernet(f.read())


def encrypt(text: str):
    return _key().encrypt(text.encode())


def decrypt(text: bytes):
    try:
        result = str(_key().decrypt(text).decode('utf-8'))
    except Exception as e:
        return e
    else:
        return result


def generate_alpha(preset: bytes):
    """Generates Alpha.key file (master password)."""
    create_in_appdata(Files.alpha_key)
    with open(appdata(Files.beta_key), 'rb') as f:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=f.read(),
            iterations=100000,
            backend=default_backend()
        )
    with open(appdata(Files.alpha_key), 'wb') as f:
        f.write(urlsafe_b64encode(kdf.derive(preset)))


def check_alpha(password: bytes):
    with open(appdata(Files.beta_key), 'rb') as f:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=f.read(),
            iterations=100000,
            backend=default_backend()
        )
    with open(appdata(Files.alpha_key), 'rb') as f:
        return urlsafe_b64encode(kdf.derive(password)) == f.read()


def generate_beta(preset: bytes):
    """Generates Beta.key file (salt)."""
    create_in_appdata(Files.beta_key)
    with open(appdata(Files.beta_key), 'wb') as f:
        f.write(preset)


def random_password(length: int = 16):
    return ''.join(choice(ascii_letters + digits + punctuation) for _ in range(length))
