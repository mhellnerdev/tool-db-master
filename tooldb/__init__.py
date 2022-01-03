from flask import Flask
import os
import json

# my_secret = os.environ['SECRET_KEY']

# with open('/etc/config.json') as config_file:
#    config = json.load(config_file)

app = Flask(__name__, template_folder='Templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


from tooldb import main, tools, wi, wip