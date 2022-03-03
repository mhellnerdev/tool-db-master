from flask import Flask
import json

# with open('/etc/config.json') as config_file:
#    config = json.load(config_file)

app = Flask(__name__, template_folder='Templates')
# app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.config['MYSQL_USER'] = 'flask_user'
app.config['MYSQL_PASSWORD'] = 'flaskpasswd'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'tooldb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


from tooldb import main, tools, wi, wip