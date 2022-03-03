import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="flask_user",
  passwd="flaskpasswd"
)

my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE tool_users")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
  print(db)
