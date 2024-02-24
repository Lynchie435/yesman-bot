import sqlite3
import os
import logging

logger = logging.getLogger('logger')

def get_database():
    try:
        db_path = './database/yesman.db'

        # Ensure the directory exists
        if not os.path.exists(os.path.dirname(db_path)):
            fullpath = os.path.dirname(db_path)
            os.makedirs(fullpath)
            logger.info(f'Database created: {db_path}')

        return db_path
    except Exception as e:
        logger.error(e)
def add_replay_to_db(filename: str, gamejson: str, playerjson: str, resultjson: str, replaysource: str, messageauthor: str, md5: str):
    try:

        logger.info(f'Adding {filename} to the SQL database')

        connection = sqlite3.connect(get_database())
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS replay_raw_data (
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
        cursor.execute('INSERT INTO replay_raw_data (filename, game_json, player_json, result_json, replay_source, user, md5) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (str(filename), str(gamejson), str(playerjson), str(resultjson), str(replaysource), str(messageauthor), str(md5)))

        connection.commit()

        # Fetch and print data
        cursor.execute('SELECT * FROM replay_raw_data')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    except sqlite3.Error as er:
            logger.error(er)

    finally:
        if connection:
            connection.close()