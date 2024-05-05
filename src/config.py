from colorama import Fore

config = {
   'watchers': {
        'libera': {
            'path': '/home/frtnx/irclogs/LiberaChat',
            'targets': ['##news.log'],
            'autoUpdate': False,
            'updateInterval': 1
        },
        'ycombinator': {
            'autoUpdate': True,
            'updateInterval': 600,
            'numPages': 5
        }
    },
    'eventStream': {
        'pickle': {
            'path': './',
            'filename': 'event_stream.pkl',
            'autoLoad': True
        }
    },
    'logging': {
        'tag_style': Fore.GREEN + 'zorb' + Fore.RESET,
        'date_style': Fore.LIGHTBLACK_EX + '%Y-%m-%d %H:%M:%S' + Fore.RESET
    }
}
