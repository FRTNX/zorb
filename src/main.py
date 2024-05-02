import os
import signal

import logging
import fastapi

from watchers.watchman import WatchMan
from event_stream import EventStream

from orb import Orb
from config import config

app = fastapi.FastAPI()

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='[zorb] %Y-%m-%d %H:%M:%S')

# the idea is to have a single event stream, imported where needed.
event_stream = EventStream(logging=logging, config=config['eventStream'])

orb = Orb(event_stream=event_stream)

watchman = WatchMan(event_stream=event_stream, config=config['watchers'], logging=logging)
watchman.deploy()

# execute after deploying watchman to benefit from retro zorb
event_stream.auto_save()

@app.get('/count')
def count():
    return { 'events': orb.count() }

@app.get('/events')
def events(keyword: str = '', source: str = ''):
    if keyword:
        return { 'events': orb.events_by_keyword(keyword) }
    
    elif source:
        return { 'events': orb.events_by_source(source) }   
    
    else:
        return { 'events': orb.events() } 

@app.get('/sources')
def sources():
    return orb.sources()

# authenticate like a mofo. possibly remove in prod
@app.get('/shutdown')
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')
