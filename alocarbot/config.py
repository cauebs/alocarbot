import json
from pathlib import Path


with open(Path.home() / '.config/alocarbot.json') as f:
    config = json.load(f)

USERNAME = config['username']
PASSWORD = config['password']
TOKEN = config['token']
DB_PATH = config['db_path']
