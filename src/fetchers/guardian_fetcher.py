from .base import ArticleFetcher


class GuardianFetcher(ArticleFetcher):
    """"""
    def _parse(self, html):
        """"""
        # make some beautiful soup!
        return html  # obviously return parsed result
    
    def fetch_article(self, url):
        response_data = requests.get(url)
        
        response_data.raise_for_status()
        html = response_data.content()
        
        result = self._parse(html)
        return result
