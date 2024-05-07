import requests
from config import config

SOURCES = []  # todo: add all supported sources here

class NewsAPI:
    """Provides watchers access to newsapi.org."""
    BASE_URL = 'https://newsapi.org'
        
    def fetch_by_source(self, source):
        """Fetches events pubished by source."""
        path = '/v2/top-headlines'
        params = { 'sources': source, 'apiKey': config['news_api']['api_key'] }
        
        response = requests.get(
            url=f'{self.BASE_URL}{path}',
            params=params,
            verify=False
        )
        
        response.raise_for_status()
        response_data = response.json()
        try:
            return response_data['articles']
        except Exception as e:
            return []
