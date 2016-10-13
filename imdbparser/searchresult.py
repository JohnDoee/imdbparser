import re

from requests.compat import quote_plus

from .base import Base
from .movie import Movie


class SearchResult(Base):
    base_url = 'http://akas.imdb.com/find?q=%s&s=tt&ttype=ft'

    def __init__(self, query, imdb):
        self.imdb_id = quote_plus(query)
        self.imdb = imdb

    def parse(self, html):
        super(SearchResult, self).parse(html)

        self.movies = []
        for movie_row in self.tree.xpath("//table[@class='findList']//tr[contains(@class, 'findResult')]"):
            cover = movie_row.xpath(".//td[@class='primary_photo']//img/@src")[0]
            if '/nopicture/' in cover:
                cover = None
            else:
                cover = self.cleanup_photo_url(cover)

            text = movie_row.xpath(".//td[@class='result_text']")[0]
            imdb_id = re.findall(r'/tt(\d+)/', text.xpath('.//a/@href')[0])[0]
            orig_title = text.xpath('.//a')[0].text
            alternative_titles = []

            base_elements = [x.strip() for x in text.xpath('./text()') if x.strip()]

            if 'aka' in base_elements:
                base_elements.remove('aka')

                alternative_titles.append(orig_title)
                orig_title = text.xpath('./i')[0].text.strip('"')

            year = None
            if base_elements:
                try:
                    year = int(base_elements[0].strip('()'))
                except ValueError:
                    pass

            movie = Movie(imdb_id, self.imdb)
            movie.title = orig_title
            movie.year = year
            movie.cover = cover
            movie.alternative_titles = alternative_titles

            self.movies.append(movie)
