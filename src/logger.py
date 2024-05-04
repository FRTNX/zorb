import logging
from colorama import Fore

tag_style = Fore.GREEN + 'zorb' + Fore.RESET
date_style = Fore.LIGHTBLACK_EX + '%Y-%m-%d %H:%M:%S' + Fore.RESET

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt=f'[{tag_style}] [{date_style}]')
