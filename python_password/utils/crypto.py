# -*- coding: utf-8 -*-
import random
import string

from cryptography.fernet import Fernet

from utils.files import file, Files, generate_salt


def encrypt(text):
    """
    Encrypts provided text with alpha password.
    :param text: Text to encrypt.
    :return: Encrypted text.
    """
    try:
        open(file(Files.beta_key))
    except FileNotFoundError:
        generate_salt()
    finally:
        try:
            open(file(Files.alpha_key))
        except FileNotFoundError:
            return None
        else:
            with open(file(Files.alpha_key), 'rb') as f:
                key = f.read()
                f = Fernet(key)
                return f.encrypt(text.encode())


def decrypt(text):
    """
    Decrypts provided text with alpha password.
    :param text: Text to decrypt.
    :return: Decrypted text or ``None`` if alpha password do not match encryption password.
    """
    pass
    # TODO - Decryption function


def rand_password(length: int = 16):
    """
    Creating a password from upper and lowercase letters, numbers and basic special characters.
    :param length: Password length (default is 16).
    :return: Very safe password.
    """
    # possibilities = list(str(string.ascii_letters + string.digits + string.punctuation))
    # result = ''
    # for i in range(length):
    #     result += random.choice(possibilities)
    # return result
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))
