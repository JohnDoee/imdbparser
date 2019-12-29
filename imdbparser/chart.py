import re
import sys
from decimal import Decimal

from requests.compat import quote_plus

from .base import Base
from .movie import Movie


class Chart(Base):
    base_url = "https://www.imdb.com/chart/%s"

    def __init__(self, chart, imdb):
        self.chart = chart
        self.imdb = imdb

    def _get_urls(self):
        return [self.base_url % (self.chart,)]

    def parse(self, htmls):
        super(Chart, self).parse(htmls)

        self.results = []
        for item_row in self.trees[0].xpath("//tbody[@class='lister-list']/tr"):
            poster_column = item_row.xpath(".//td[@class='posterColumn']")[0]

            cover = poster_column.xpath(".//img/@src")[0]
            if "/nopicture/" in cover:
                cover = None
            else:
                cover = self.cleanup_photo_url(cover)

            imdb_id = re.findall(r"/tt(\d+)/", poster_column.xpath(".//a/@href")[0])[0]

            rating_text = item_row.xpath(
                ".//td[contains(@class, 'imdbRating')]/strong/@title"
            )
            if rating_text:
                print(rating_text[0])
                rating, votes = re.findall("[0-9.,]+", rating_text[0])
                rating = Decimal(rating)
                votes = int(votes.replace(",", ""))

            year = None
            for base_element in item_row.xpath(
                ".//td[@class='titleColumn']//span[@class='secondaryInfo']/text()"
            ):
                years = re.findall(r"\((\d{4})\)", base_element)
                if years:
                    year = int(years[0])
                    break

            item = Movie(imdb_id, self.imdb)

            item.title = item_row.xpath(".//td[@class='titleColumn']//a/text()")[0]
            item.year = year
            item.cover = cover
            item.rating = rating
            item.votes = votes

            self.results.append(item)
