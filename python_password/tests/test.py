# -*- coding: utf-8 -*-
import os

from python_password.PyPassword import encrypt, query, random_password, appdata


def test_encrypt():
    for i in range(1000):
        for name in ['a' * x for x in range(32)]:
            assert name != encrypt(name), 'test failed, encryption does not work'


def test_sqlite():
    for i in range(100):
        assert query('SELECT sqlite_version();') is not None, 'test failed, can not connect to database'


def test_random_password():
    for i in range(100000):
        assert random_password() != random_password(), 'test failed, random passwords are the same'


def test_access_file():
    for i in range(100):
        for name in ['a' * x for x in range(255)]:
            filename = appdata(name)[-(len('PyPassword')+len(os.sep)+len(name))::]
            assert filename == f'PyPassword{os.sep}{name}', f'test failed because ``u_filename`` is {filename}'
