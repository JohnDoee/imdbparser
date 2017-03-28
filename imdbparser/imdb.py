import re

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

    def _normalize_title(self, title):
        title = re.sub(r'[^\x00-\x7F]+', '', title)
        title = re.sub(r' +', ' ', title)

        return title

    def resolve_movie(self, title, year=None):
        """Tries to find a movie with a given title and year"""
        r = self.search_movie(title)

        return self._match_results(r, title, year)

    def resolve_tv_show(self, title, year=None):
        """Tries to find a movie with a given title and year"""
        r = self.search_tv_show(title)

        return self._match_results(r, title, year)

    def _match_results(self, results, title, year):
        results.fetch()
        results = results.results

        if not results:
            return None

        normalized_title = self._normalize_title(title)

        for result in results[:7]:
            for title in result.get_titles():
                result_normalized_title = result.title
                if result_normalized_title == normalized_title and (year is None or result.year is None or year == result.year):
                    return result

        if year:
            for result in results[:5]:
                for title in result.get_titles():
                    result_normalized_title = result.title
                    if result_normalized_title == normalized_title and result.year is not None and abs(year - result.year) <= 1:
                        return result

        return results[0]

    def search_movie(self, query):
        return SearchResult('movie', query, self)

    def search_tv_show(self, query):
        return SearchResult('tv', query, self)

    def get_movie(self, imdb_id):
        return Movie(imdb_id, self)

    def get_person(self, imdb_id):
        return Person(imdb_id, self)
