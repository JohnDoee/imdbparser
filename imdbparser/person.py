from .base import Base


class Person(Base):
    name = None

    base_url = 'http://akas.imdb.com/name/nm%s/'

    def parse(self, html):
        super(Person, self).parse(html)

    def __repr__(self):
        return '<Person fetched=%r imdb_id=%r name=%r>' % (self.fetched, self.imdb_id, self.name)
