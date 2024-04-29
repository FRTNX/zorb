from .base import ArticleFetcher
from .guardian_fetcher import GuardianFetcher

MAPPER = {
    'the guardian': GuardianFetcher     
}

def get_fetcher(fetcher_name: str) -> ArticleFetcher:
    return MAPPER.get(fetcher_name)
 