from flask import render_template
from tooldb import app
import mysql.connector

# # MySQL connection string
# def createConnection(host):
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host = "localhost",
#             user = "flask_user",
#             passwd = "flaskpasswd",
#             db = "tool-db-master"
#             )
#         print("Connection to MySQL DB successful")
#     except Error as e:
#         print(f"The error '{e}' occurred")
#     return connection


# MySQL connection string
def createConnection(host):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = "localhost",
            user = "flask_user",
            passwd = "flaskpasswd",
            db = "tool-db-master"
            )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection








def executeQuery(connection, query, input):
    cursor = connection.cursor()
    try:
        cursor.execute(query, input)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def executeReadQuery(connection, query, input):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, input)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def executeReadQueryAll(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


# old connection string to local sqlite (tooling-db-db)
# connection = createConnection("tooldb/tooling-db.db")

# new connection to local mysql db (tooling-db-db)
connection = createConnection("mysql://flask_user:flaskpasswd@localhost/tool_users")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tabletest")
def tabletest():
    return render_template("tableTest.html")
