#!/usr/bin/env python3
# command-line client. 
import requests
from argparse import ArgumentParser

BASE_URL = 'http://127.0.0.1:8000'   # replace with external url if zorb not local

parser = ArgumentParser(description='Query events from zorb event stream.')
parser.add_argument('-k', '--keyword', type=str,
    help='Fetch events that include keyword.')
args = parser.parse_args()

if __name__ == '__main__':
    if args.keyword:
        path = '/events'
        params = { 'keyword': args.keyword }
        response = requests.get(url=f'{BASE_URL}{path}', params=params)
        
        response.raise_for_status()
        response_data = response.json()
        if response_data:
            for event in response_data['events']:
                print('[*] >', event['_title'])
