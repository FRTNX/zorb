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

# parser = ArgumentParser("Query Zorb's event stream.")
# parser.add_argument('-c', '--count', action='store_true', help='Return number of events in event stream.')
# parser.add_argument('-k', '--keyword', type=str, help='Search events by keyword.')
# parser.add_argument('-s', '--source', type=str, help='Search events by source.')

app = FastAPI()

@app.get('/count')
def count():
    return { 'events': orb.count() }

# if __name__ == '__main__':
#     orb = Orb(event_stream=event_stream)
#     # args = parser.parse_args()
    
#     while True:
#         user_input = input('[zorb] > ')
        
#         if user_input == 'count':
#             print(orb.count())

#         elif user_input.startswith('-kw '):
#             keyword = user_input[3:]
#             print(list(orb.events_by_keyword(keyword)))
            
#         elif user_input.startswith('-s '):
#             source = user_input[2:]
#             print(orb.events_by_source(source))    

#         else:
#             print('Unrecognised command.')

