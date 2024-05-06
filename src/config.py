from colorama import Fore

# Contaiins application-wide configurations. Using a python file for
# the versatility: comments, transformations, etc.
config = {
   'watchers': {
        'libera': {
            'path': '/home/frtnx/irclogs/LiberaChat',
            'targets': ['##news.log'],
            'update_interval': 1
        },
        'ycombinator': {
            'update_interval': 60 * 5,       # every 5 minutes
            'num_pages': 5
        },
        'techcrunch': {
            'update_interval': 60 * 30,      # every 30 minutes
            'num_pages': 5
        }
    },
    'event_stream': {
        'pickle': {
            'path': './',
            'filename': 'event_stream.pkl',
            'auto_load': True
        }
    },
    'logging': {
        'tag_style': Fore.GREEN + 'zorb' + Fore.RESET,
        'date_style': Fore.LIGHTBLACK_EX + '%Y-%m-%d %H:%M:%S' + Fore.RESET
    }
}
