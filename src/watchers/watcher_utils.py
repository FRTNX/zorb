import requests

def online():
    try:
        response = requests.get('http://www.msftncsi.com/ncsi.txt')
        response.raise_for_status()
        return True
    except Exception as e: # because for some reason ConnectionError wasn't being caught
        return False

