import sqlite3
import os
import logging

logger = logging.getLogger('logger')


def get_database():
    try:
        db_path = '../database/yesman.db'

        # Ensure the directory exists
        if not os.path.exists(os.path.dirname(db_path)):
            fullpath = os.path.dirname(db_path)
            os.makedirs(fullpath)
            logger.info(f'Database created: {db_path}')

        return db_path
    except Exception as e:
        logger.error(e)


def add_replay_to_db(filename: str, gamejson: str, playerjson: str, resultjson: str, replaysource: str,
                     messageauthor: str, md5: str):
    try:

        logger.info(f'Adding {filename} to the database')

        connection = sqlite3.connect(get_database(), timeout=30)
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS tbl_replay_raw_data (
                            id INTEGER PRIMARY KEY,
                            filename TEXT,
                            game_json TEXT,
                            player_json TEXT,
                            result_json TEXT,
                            replay_source TEXT,
                            user TEXT,
                            md5 TEXT
                          )''')

        # INSERT INTO
        cursor.execute(
            'INSERT INTO tbl_replay_raw_data (filename, game_json, player_json, result_json, replay_source, user, md5) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (str(filename), str(gamejson), str(playerjson), str(resultjson), str(replaysource), str(messageauthor),
             str(md5)))

        connection.commit()

    except sqlite3.Error as er:
        logger.error(er)

    finally:
        if connection:
            connection.close()

def get_whois(username: str):
    try:
        logger.debug(f'Adding usernames to the database')

        connection = sqlite3.connect(get_database())
        cursor = connection.cursor()

        # Select top 5 rows where the username is like "john" ordered by id
        cursor.execute('''
            SELECT rank, elo, userid, username, start_date, end_date, is_current
            FROM tbl_usernames
            WHERE username LIKE ?
            ORDER BY id DESC
            LIMIT 5
        ''', (f'%{username}%',))

        # Fetch the results
        result = cursor.fetchall()
        return result
    except sqlite3.Error as er:
        logger.error(er)

    finally:
        if connection:
            connection.close()