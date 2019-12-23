import re
import sys

from requests.compat import quote_plus

from .base import Base
from .movie import Movie


class SearchResult(Base):
    base_url = "http://www.imdb.com/find?q=%s&s=tt"

    def __init__(self, search_type, query, imdb):
        self.search_type = search_type
        if sys.version_info[0] < 3 and isinstance(query, unicode):
            query = query.encode("utf-8")
        self.imdb_id = quote_plus(query)
        self.imdb = imdb

    def _get_urls(self):
        url = self.base_url
        if self.search_type == "tv":
            url += "&ttype=tv"
        elif self.search_type == "movie":
            url += "&ttype=ft"

        return [url % (self.imdb_id,)]

    def parse(self, htmls):
        super(SearchResult, self).parse(htmls)

        self.results = []
        for movie_row in self.trees[0].xpath(
            "//table[@class='findList']//tr[contains(@class, 'findResult')]"
        ):
            cover = movie_row.xpath(".//td[@class='primary_photo']//img/@src")[0]
            if "/nopicture/" in cover:
                cover = None
            else:
                cover = self.cleanup_photo_url(cover)

            text = movie_row.xpath(".//td[@class='result_text']")[0]
            imdb_id = re.findall(r"/tt(\d+)/", text.xpath(".//a/@href")[0])[0]
            orig_title = text.xpath(".//a")[0].text
            alternative_titles = []

            base_elements = [x.strip() for x in text.xpath("./text()") if x.strip()]

            if "aka" in base_elements:
                base_elements.remove("aka")

                alternative_titles.append(orig_title)
                orig_title = text.xpath("./i")[0].text.strip('"')

            year = None
            if base_elements:
                try:
                    years = re.findall(r"\((\d{4})\)", base_elements[0])
                    if years:
                        year = int(years[0])
                except ValueError:
                    pass

            movie = Movie(imdb_id, self.imdb)
            movie.title = orig_title
            movie.year = year
            movie.cover = cover
            movie.alternative_titles = alternative_titles

            self.results.append(movie)
