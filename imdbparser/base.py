import logging

import lxml.html

logger = logging.getLogger(__name__)


class Base(object):
    fetched = False

    def __init__(self, imdb_id, imdb):
        self.imdb_id = str(imdb_id).zfill(7)
        self.imdb = imdb

    def _get_url(self):
        return self.base_url % (self.imdb_id, )

    def fetch(self):
        if not self.fetched:
            url = self._get_url()
            logger.debug('Fetching and parsing url %s' % (url, ))
            self.parse(self.imdb._get_data(url))

    def cleanup_photo_url(self, url):
        if url:
            if 'title_addposter' in url or 'imdb-share-logo' in url:
                return None
            logger.debug('Cleaning up url %s' % (url, ))
            url = url.split('.')
            url.pop(-2)
            return '.'.join(url)

    def parse(self, html):
        self.tree = lxml.html.fromstring(html)
