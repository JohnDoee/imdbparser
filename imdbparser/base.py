import logging

import lxml.html

logger = logging.getLogger(__name__)


class Base(object):
    fetched = False

    def __init__(self, imdb_id, imdb):
        self.imdb_id = str(imdb_id).zfill(7)
        self.imdb = imdb

    def _get_urls(self):
        return [base_url % (self.imdb_id,) for base_url in self.base_urls]

    def fetch(self):
        if not self.fetched:
            urls = self._get_urls()
            logger.debug("Fetching and parsing urls %s" % (urls,))
            self.parse([self.imdb._get_data(url) for url in urls])
            self.fetched = True

    def cleanup_photo_url(self, url):
        if url:
            if "title_addposter" in url or "imdb-share-logo" in url:
                return None
            url = url.split(".")
            url.pop(-2)
            return ".".join(url)

    def parse(self, htmls):
        self.trees = [lxml.html.fromstring(html) for html in htmls]
