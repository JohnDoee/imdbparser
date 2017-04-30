import logging
import re
from decimal import Decimal

from .base import Base
from .person import Person

logger = logging.getLogger(__name__)


class Movie(Base):
    title = None
    year = None

    base_urls = ['http://akas.imdb.com/title/tt%s/combined', 'http://akas.imdb.com/title/tt%s/']

    def parse(self, htmls):
        super(Movie, self).parse(htmls)

        self.alternative_titles = []
        self.actors = []
        self.directors = []
        self.writers = []

        self.languages = []
        self.genres = []
        self.countries = []
        self.plot_keywords = []

        self.cover = None
        self.duration = None
        self.title = None
        self.year = None
        self.release_date = None
        self.description = None
        self.plot = None
        self.storyline = None

        titles = [x.strip() for x in self.trees[0].xpath('//div[@id="tn15title"]/h1//text()') if x.strip() and x not in ['(', ')']]

        self.title = titles[0]
        if self.title[0] == self.title[-1] == '"':
            self.title = self.title[1:-1]

        title_extra = self.trees[0].xpath("//h1/span[@class='title-extra']")
        if title_extra:
            extra_title = title_extra[0].text.strip()
            if extra_title[0] == extra_title[-1] == '"':
                extra_title = extra_title[1:-1]

            if title_extra[0].xpath(".//i[text()='(original title)']"):
                self.alternative_titles.append(self.title)
                self.title = extra_title
            else:
                self.alternative_titles.append(extra_title)

        for t in titles[1:]:
            try:
                self.year = int(t.strip(u'()').split(u'\u2013')[0])
            except ValueError:
                continue
            else:
                break
        else:
            header_title = self.trees[0].xpath("//meta[@name='title']/@content")
            if header_title:
                try:
                    self.year = int(re.findall(r'\((?:TV Series )?(\d{4})(?:\u2013(?: |\d+))?\) - IMDb$',
                                               header_title[0])[0])
                except (ValueError, IndexError):
                    pass

        aggregate_ratings = self.trees[1].xpath("//div[@itemprop='aggregateRating']")
        if aggregate_ratings:
            aggregate_rating = aggregate_ratings[0]
            self.rating = Decimal(aggregate_rating.xpath(".//*[@itemprop='ratingValue']/text()")[0])
            self.votes = int(aggregate_rating.xpath(".//*[@itemprop='ratingCount']/text()")[0].replace(',', ''))

        descriptions = self.trees[1].xpath("//div[@itemprop='description']")
        if descriptions:
            self.storyline = '\n'.join([x.strip() for x in descriptions[-1].xpath('.//text()') if x.strip()]).strip()

        cover = self.trees[0].xpath("//link[@rel='image_src']/@href")
        if cover:
            self.cover = self.cleanup_photo_url(cover[0])

        for elem in self.trees[0].xpath("//div[@class='info']"):
            info_text = elem.xpath(".//h5")[0].text
            if not info_text:
                continue
            info_content = elem.xpath(".//div[@class='info-content']")[0]

            if info_text == 'Release Date:':
                self.release_date = info_content.text.strip()
            elif info_text == 'Genre:':
                self.genres = [x.text for x in info_content.xpath('.//a') if '/Genres/' in x.attrib['href']]
            elif info_text == 'Tagline:':
                self.description = info_content.text.strip()
            elif info_text == 'Plot:':
                self.plot = info_content.text.strip(' |\n')
            elif info_text == 'Plot Keywords:':
                self.plot_keywords = [x.text for x in info_content.xpath(".//a") if '/keyword/' in x.attrib['href']]
            elif info_text == 'Also Known As:':
                for elem in info_content.xpath("./text()"):
                    title = elem.strip().split('"')
                    if len(title) > 2 and len(title[0]) == 0:
                        self.alternative_titles.append('"'.join(title[1:-1]))
            elif info_text == 'Runtime:':
                runtimes = re.findall('(\d+) min', info_content.text)
                if runtimes:
                    self.duration = int(runtimes[0])
            elif info_text == 'Country:':
                self.countries = [x.text for x in info_content.xpath(".//a") if '/country/' in x.attrib['href']]
            elif info_text == 'Language:':
                self.languages = [x.text for x in info_content.xpath(".//a") if '/language/' in x.attrib['href']]
            elif info_text == 'Company:':
                self.companies = [x.text for x in info_content.xpath(".//a") if '/company/' in x.attrib['href']]
            elif info_text.startswith('Director'):
                for elem in info_content.xpath(".//a"):
                    if '/name/' not in elem.attrib['href']:
                        continue
                    p = Person(re.findall('/nm(\d+)', elem.attrib['href'])[0], self.imdb)
                    p.name = elem.text
                    self.directors.append(p)
            elif info_text.startswith('Writer'):
                for elem in info_content.xpath(".//a"):
                    if '/name/' not in elem.attrib['href']:
                        continue
                    p = Person(re.findall('/nm(\d+)', elem.attrib['href'])[0], self.imdb)
                    p.name = elem.text
                    self.writers.append(p)

        if not self.release_date:
            release_dates = [x.strip() for x in self.trees[1].xpath("//h4[text()='Release Date:']/../text()") if x.strip()]
            if release_dates:
                self.release_date = release_dates[0]

        for elem in self.trees[0].xpath("//table[@class='cast']/tr"):
            elem = elem.xpath(".//td[@class='nm']/a")
            if not elem:
                break
            elem = elem[0]

            p = Person(re.findall('/nm(\d+)', elem.attrib['href'])[0], self.imdb)
            p.name = elem.text
            self.actors.append(p)

        self.alternative_titles = list(set(self.alternative_titles))

    def __repr__(self):
        return '<Movie fetched=%r imdb_id=%r title=%r year=%r>' % (self.fetched, self.imdb_id, self.title, self.year)

    def get_titles(self):
        yield self.title
        for title in self.alternative_titles:
            yield title
