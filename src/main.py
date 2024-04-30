import logging
from watchers.watchman import WatchMan

from event_stream import EventStream
from orb import Orb

from fastapi import FastAPI
from config import config

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='[zorb] %Y-%m-%d %H:%M:%S')

# the idea is to have a single event stream, imported where needed.
event_stream = EventStream(logging=logging)
     
watchman = WatchMan(event_stream=event_stream, config=config['watchers'], logging=logging)
watchman.deploy()

orb = Orb(event_stream=event_stream)

app = FastAPI()

@app.get('/count')
def count():
    return { 'events': orb.count() }
