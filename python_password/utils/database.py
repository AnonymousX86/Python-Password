# -*- coding: utf-8 -*-
from sqlite3 import connect

from python_password.utils.files import appdata, Files, create_in_appdata


def generate_sqlite():
    create_in_appdata(Files.sqlite)
    for q in [
        '''create table passwords(id INTEGER constraint passwords_pk primary key autoincrement, name varchar not null,
        password varchar not null );''',
        'create unique index passwords_name_uindex on passwords (name);'
    ]:
        query(q)


def query(q_input: str, q_args=None):
    """
    Executes query in SQLite database.
    :param q_input: SQL query.
    :param q_args: Query arguments (replaces ``?`` symbols in query).
    :return: All records or ``None`` if nothing is matching query.
    """
    # TODO - Include SQLAlchemy
    if q_args is None:
        q_args = []
    create_in_appdata(Files.sqlite)
    with connect(appdata(Files.sqlite)) as conn:
        my_cursor = conn.cursor()
        my_cursor.execute(q_input, q_args)
        records = my_cursor.fetchall()
        conn.commit()
        return records


def already_exists(alias: str):
    return True if len(query(
        'SELECT `name` FROM `passwords` WHERE `name` LIKE ?;',
        [alias]
    )) > 0 else False


def save_password(alias: str, value: bytes):
    query(
        'INSERT INTO `passwords` (`name`, `password`) VALUES (?, ?);',
        [alias, value]
    )


def get_one_password(alias: str):
    q = query(
        'SELECT `password` FROM `passwords` WHERE `name` LIKE ?;',
        [alias]
    )
    return None if q is None else q[0][0]


def gel_all_passwords():
    return query('SELECT `name`, `password` FROM `passwords`;')


def del_password(alias: str):
    query(
        'DELETE FROM `passwords` WHERE `name` LIKE ?;',
        [alias]
    )
