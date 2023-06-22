import random
import string
import mysql.connector

host = "d26893.mysql.zonevs.eu"
user = "d26893_smirnov"
password = "GxnvlPQL8MA21PfZSRQF"
database = "d26893_smirnov"

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor()
        return connection, cursor
    except mysql.connector.Error as error:
        return 'Error: {}'.format(error)

def Create_table():
    connection, cursor = create_connection()
    table_name = "user_data_from_tg"
    sql = 'CREATE TABLE IF NOT EXISTS {} (UserID INT NOT NULL UNIQUE PRIMARY KEY, UserToken CHAR(25) UNIQUE, PCToken CHAR(25), PC_Application_status CHAR(7) DEFAULT "None")'.format(table_name)
    cursor.execute(sql)
    connection.commit()

def TokenGenerator():
    connection, cursor = create_connection()
    token = None
    while not token:
        token = []
        for i in range(10):
            token.append(str(random.randint(0, 9)))
            token.append(random.choice(string.ascii_letters))
        token = "".join(token)
        query = "SELECT UserID FROM user_data_from_tg WHERE UserToken = %s"
        cursor.execute(query, (token,))
        result = cursor.fetchone()
        if result:
            print(f'Generated token {token} already exist in {result}\n generating new token for user {result}')
            token = None

    return token


def DataChecker(User_Id):
    conn, cursor = create_connection()
    query = "SELECT UserToken, PCToken FROM user_data_from_tg WHERE UserID = %s"
    cursor.execute(query, (User_Id,))
    result = cursor.fetchone()
    if result:
        user_token, pc_token = result
        if pc_token:
            print(f"User {User_Id} already has a PC token: {pc_token}")

            return "That is Your token -> "+ user_token +"\nOur system detected that you have a connected PC id -> " + pc_token
        else:
            print(f"User {User_Id} already has a token: {user_token}")
            return "That is Your token -> "+ user_token +"\n⚠⚠You have not yet connected your computer to an account\n Use this link for install ->"
    else:
        token = TokenGenerator()
        query = "INSERT INTO user_data_from_tg (UserID, UserToken) VALUES (%s, %s)"
        cursor.execute(query, (User_Id, token))
        conn.commit()
        return token

def USER_PC_DATA(User_Id):
    connection, cursor = create_connection()
    query = "SELECT PCToken FROM user_data_from_tg WHERE UserID = %s"
    cursor.execute(query, (User_Id,))
    PCToken = cursor.fetchone()[0]
    table_name = f'PCID_{PCToken}'
    try:
        sql = 'SELECT Application, Path, size, memory, Status, Favorite FROM {}'.format(table_name)
        cursor.execute(sql)
        data = cursor.fetchall()
        result = {}
        for row in data:
            result[row[0]] = {'Path': row[1], 'size': row[2], 'memory': row[3], 'Status': row[4], 'Favorite': row[5]}
        return result
    except mysql.connector.errors.ProgrammingError:
        print(f'ERROR:{User_Id} have no applications')
        return False

def PC_Application_status_observer(User_Id):
    connection, cursor = create_connection()
    query = "SELECT PC_Application_status FROM user_data_from_tg WHERE UserID = %s"
    cursor.execute(query, (User_Id,))
    PC_status = cursor.fetchone()[0]
    if PC_status == "Online":
        return 2
    elif PC_status == "Offline":
        return 1
    else:
        return 0

def Switch_changer(User_Id, Application):
    connection, cursor = create_connection()
    query = "SELECT PCToken FROM user_data_from_tg WHERE UserID = %s"
    cursor.execute(query, (User_Id,))
    PCToken = cursor.fetchone()[0]
    table_name = f'PCID_{PCToken}'

    update_query = f"UPDATE {table_name} SET switcher = 1 WHERE Application = %s"
    cursor.execute(update_query, (Application,))
    connection.commit()  # Remember to commit the changes
    cursor.close()
    connection.close()
