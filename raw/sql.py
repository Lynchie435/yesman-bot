import json

#import mysql.connector
#from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()

# def establish_connection():
#     try:
#         # Get the connection string from environment variables
#         host = os.getenv('MYSQLDBHOST')
#         database = os.getenv('MYSQLDATABASE')
#         user = os.getenv('MYSQLDBUSER')
#         password = os.getenv('MYSQLDBPWD')
#
#         # Define the connection parameters
#         connection_params = {
#             'host': host,
#             'database': database,
#             'user': user,
#             'password': password
#         }
#
#         # Establish database connection using the connection string
#         connection = mysql.connector.connect(**connection_params)
#         if connection.is_connected():
#             return connection
#     except Error as e:
#         print("Error:", e)
#         return None
#
#
# def add_replay_to_db(filename, gamejson, playerjson, resultjson, replaysource, messageauthor):
#     try:
#
#         connection = establish_connection()
#
#         if connection:
#
#             # Define the update query
#             update_query = f"INSERT INTO `yesman`.`replay_raw_data` (`filename`, `game_json`, `player_json`, `result_json`, `replay_source`, `user`) VALUES (%s,%s ,%s ,%s ,%s, %s);"
#
#             # Execute the query with parameters
#             cursor = connection.cursor()
#             cursor.execute(update_query, (filename, json.dumps(gamejson),json.dumps(playerjson),json.dumps(resultjson),replaysource, messageauthor))
#
#             # Commit the changes
#             connection.commit()
#
#         print("Update successful")
#     except Error as e:
#         print("Error:", e)
#     finally:
#         cursor.close()

def add_replay_to_db(filename, gamejson, playerjson, resultjson, replaysource, messageauthor):
    try:

        #connection = establish_connection()
        #
        # if connection:

            # Define the update query
        update_query = f"INSERT INTO `yesman`.`replay_raw_data` (`filename`, `game_json`, `player_json`, `result_json`, `replay_source`, `user`) VALUES (%s,%s ,%s ,%s ,%s, %s);"

        with open("db_log.txt", "a") as file:
            # Append the variable's value to the file
            file.write(update_query + "\n")

            # # Execute the query with parameters
            # cursor = connection.cursor()
            # cursor.execute(update_query, (filename, json.dumps(gamejson),json.dumps(playerjson),json.dumps(resultjson),replaysource, messageauthor))
            #
            # # Commit the changes
            # connection.commit()
    except Exception as e:
        print(e)
    #     print("Update successful")
    # except Error as e:
    #     print("Error:", e)
    # finally:
    #     cursor.close()
