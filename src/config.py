import os
from dotenv import load_dotenv
from colorama import Fore

load_dotenv()

# Contaiins application-wide configurations. Using a python file for
# the versatility: comments, transformations, etc.
config = {
   'watchers': {
       # using http://www.msftncsi.com/ncsi.txt for connectivity pings costs
       # 2 kilobytes per ping. target zorb uptime is about 12 hours, so calling once
       # every minute results in 1440KB used for connection tests per 12 hour session.
       # todo: find sites/api's with response size < 2KB and test every 30 seconds
        'connection_test_interval': 60,      # every 60 seconds
        'libera': {
            'path': '/home/frtnx/irclogs/LiberaChat',
            'targets': ['##news.log'],
            'update_interval': 1
        },
        'ycombinator': {
            'update_interval': 60 * 5,       # every 5 minutes
            'num_pages': 2
        },
        'techcrunch': {
            'update_interval': 60 * 30,      # every 30 minutes
            'num_pages': 1
        },
        'al_jezeera': {
            'update_interval': 15,
            'source_id': 'al-jazeera-english'
        }
    },
    'event_stream': {
        'pickle': {
            'path': './',
            'filename': 'event_stream.pkl',
            'auto_load': True,
            'meta': {
                'path': './',
                'filename': 'event_stream_meta.json'
            }
        }
    },
    'logging': {
        'tag_style': Fore.GREEN + 'zorb' + Fore.RESET,
        'date_style': Fore.LIGHTBLACK_EX + '%Y-%m-%d %H:%M:%S' + Fore.RESET
    },
    # The Shogun API is a closed-source extension of zorb that deals with extracting
    # events from external sites
    'shogun_api': {
        'api_key': os.getenv('SHOGUN_API_KEY')
    }
}
