from flask import Flask
import json

# with open('/etc/config.json') as config_file:
#    config = json.load(config_file)

app = Flask(__name__, template_folder='Templates')
# app.config['SECRET_KEY'] = config.get('SECRET_KEY')

from tooldb import main, tools, wi, wip