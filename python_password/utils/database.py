# -*- coding: utf-8 -*-
import sqlite3

from kivy import Logger

from utils.files import appdata, Files, generate_appdata


def generate_sqlite():
    """Creates SQLite database."""
    try:
        generate_appdata()
        open(appdata(Files.sqlite), 'x')
    except FileExistsError:
        pass
    else:
        Logger.info(f'Database: {Files.sqlite}.db file not found, creating it.')
    finally:
        query('''create table passwords(id INTEGER constraint passwords_pk primary key autoincrement, name varchar not
                 null, password varchar not null );''')
        query('create unique index passwords_name_uindex on passwords (name);')


def query(q_input: str, q_args=None):
    """
    Executes query in SQLite database.
    :param q_input: SQL query.
    :param q_args: Query arguments (replaces ``?`` symbols in query).
    :return: All records or ``None`` if nothing is matching query.
    """
    if q_args is None:
        q_args = []
    try:
        open(appdata(Files.sqlite))
    except FileNotFoundError:
        generate_sqlite()
    finally:
        with sqlite3.connect(appdata(Files.sqlite)) as conn:
            my_cursor = conn.cursor()
            try:
                my_cursor.execute(q_input, q_args)
            except sqlite3.OperationalError:
                generate_sqlite()
                # When database is created of course there will be no matching values.
                return None
            else:
                Logger.info('Database: Accessing SQLite with query:')
                Logger.info(f'Database: "{q_input}".')
                if q_args:
                    Logger.info('Database: With arguments:')
                    Logger.info(f'Database: "{q_args}".')
                records = my_cursor.fetchall()
                conn.commit()
                return records


def sort_nested(n_list: list, index=0):
    """
    Sorting alphabetically list of list by key in nested list.
    :argument n_list: List of lists - [[...], [...], [...]].
    :argument index: Which element of nested list should be a key.
    :return: Sorted list by elements in nested lists.
    """
    return sorted(n_list, key=lambda x: x[index])
