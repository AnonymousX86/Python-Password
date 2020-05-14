# -*- coding: utf-8 -*-
from python_password.PyPassword import encrypt, query, rand_password, file


def test_encrypt():
    origin = 'Foo Bar Baz'
    assert origin != encrypt(origin), 'test failed, encryption does not work'


def test_sqlite():
    q = query('SELECT sqlite_version();')
    assert q is not None, 'test failed, can not connect to database'


def test_random_password():
    foo = rand_password()
    bar = rand_password()
    assert foo != bar, 'test failed, random passwords are the same'


def test_access_file():
    for name in ('foo', 'bar'):
        p_filename = file(name, 'p')[-19::]
        assert p_filename == f'PyPassword_data/{name}', f'test failed because ``p_filename`` is {p_filename}'

        u_filename = file(name)[-14::]  # Default 'u' option
        assert u_filename == f'PyPassword/{name}', f'test failed because ``u_filename`` is {u_filename}'
