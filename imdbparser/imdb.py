import requests

from .movie import Movie
from .person import Person
from .searchresult import SearchResult


class IMDb(object):
    def _get_data(self, url):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
        }
        r = requests.get(url, headers=headers)
        return r.text

    def search_movie(self, query):
        return SearchResult(query, self)

    def get_movie(self, imdb_id):
        return Movie(imdb_id, self)

    def get_person(self, imdb_id):
        return Person(imdb_id, self)
