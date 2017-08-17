from pathlib import Path
import json


with open(Path.home() / '.config') as f:
    config = json.load(f)

USERNAME = config['username']
PASSWORD = config['password']
TOKEN = config['token']
