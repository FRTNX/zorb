import os
import json

config = {}

cwd = os.getcwd()
with open(os.path.join(cwd, 'config.json')) as file:
    config = json.loads(file.read())
