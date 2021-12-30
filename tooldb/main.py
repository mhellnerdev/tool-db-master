from flask import render_template
from tooldb import app
import sqlite3
from sqlite3 import Error

def createConnection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def executeQuery(connection, query, input):
    cursor = connection.cursor()
    try:
        cursor.execute(query,input)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def executeReadQuery(connection, query, input):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query,input)
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

connection = createConnection("tooldb/tooling-db.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tabletest")
def tabletest():
    return render_template("tableTest.html")

