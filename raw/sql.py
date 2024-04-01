import json
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

def get_whois():
    try:
        connection = sqlite3.connect(get_database())
        cursor = connection.cursor()

        # Fetch data from the table
        cursor.execute('''
            SELECT tbl_usernames.id AS id,
            tbl_usernames.rank AS rank,
            tbl_usernames.elo AS elo,
            tbl_usernames.userid AS userid,
            tbl_usernames.username AS username,
            tbl_usernames.start_date AS start_date,
            tbl_usernames.end_date AS nd_date,
            tbl_usernames.is_current AS is_current, 
            tbl_usernames_additional.known_as AS known_as
            FROM tbl_usernames
            LEFT OUTER JOIN tbl_usernames_additional 
            ON tbl_usernames.userid = tbl_usernames_additional.userid
            ORDER BY id DESC
        ''')

        rows = cursor.fetchall()

        # Get column names for tbl_usernames
        cursor.execute("PRAGMA table_info(tbl_usernames)")
        columns_tbl_usernames = [column[1] for column in cursor.fetchall()]
        columns_tbl_usernames_additional = ['known_as']

        # Close the connection
        connection.close()

        # Prepare the data as a list of dictionaries
        data = []
        for row in rows:
            data.append(dict(zip(columns_tbl_usernames + columns_tbl_usernames_additional, row)))

        # Convert data to JSON format
        json_data = data

        return json_data

    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if connection:
            connection.close()