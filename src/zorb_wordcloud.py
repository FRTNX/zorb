#!/usr/bin/python
# must be python 3.8+
import re
import requests

from datetime import datetime
import matplotlib.pyplot as plt

from wordcloud import WordCloud

BASE_URL = 'http://127.0.0.1:8000'

def main():
    """Generate a wordcloud from the current event stream. Requires Python 3.8+"""
    regex = re.compile('[^a-zA-Z ]')  
    path = '/events'
    
    response = requests.get(f'{BASE_URL}{path}')
    response.raise_for_status()
    response_data = response.json()
    
    data = [event['title'] for event in response_data['events']]
    words = []
    for event in data:
        words += regex.sub('', event).split()
        
    word_string = ' '.join(words)
    wordcloud = WordCloud(width=1000, height=500).generate(word_string)
    
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.savefig(f'zorb_wordcloud-{datetime.now()}.png', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    main()
