import logging
import re
from decimal import Decimal

from .base import Base
from .person import Person

logger = logging.getLogger(__name__)


class Movie(Base):
    title = None
    year = None

    base_urls = [
        "https://www.imdb.com/title/tt%s/reference",
        "https://www.imdb.com/title/tt%s/",
    ]

    def parse(self, htmls):
        super(Movie, self).parse(htmls)

        self.alternative_titles = []
        self.actors = []
        self.directors = []
        self.writers = []
        self.more_like_this = []

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
        self.tagline = None
        self.rating = None
        self.votes = None

        titles = [
            x.strip()
            for x in self.trees[0].xpath('//h3[@itemprop="name"]//text()')
            if x.strip() and x not in ["(", ")"]
        ]

        self.title = titles[0]

        title_extra = [
            x.strip()
            for x in self.trees[0].xpath(
                "//div[@class='titlereference-header']/div/text()"
            )
            if x.strip()
        ]
        if title_extra:
            title_extra = title_extra[0]
            if title_extra != "Reference View":
                if self.trees[0].xpath(
                    "//span[@class='titlereference-original-title-label']"
                ):
                    self.alternative_titles.append(self.title)
                    self.title = title_extra
                else:
                    self.alternative_titles.append(title_extra)

        for t in titles[1:]:
            try:
                self.year = int(t.strip(u"()").split(u"\u2013")[0])
            except ValueError:
                continue
            else:
                break
        else:
            header_title = self.trees[0].xpath("//meta[@name='title']/@content")
            if header_title:
                try:
                    self.year = int(
                        re.findall(
                            r"\((?:TV Series )?(\d{4})(?:\u2013(?: |\d+))?\) - IMDb$",
                            header_title[0],
                        )[0]
                    )
                except (ValueError, IndexError):
                    pass

        cover = self.trees[0].xpath("//link[@rel='image_src']/@href")
        if cover:
            self.cover = self.cleanup_photo_url(cover[0])
            if "images/logos/imdb_fb_logo" in self.cover:
                self.cover = None

        rating = self.trees[0].xpath("//span[@class='ipl-rating-star__rating']/text()")
        if rating and rating[0]:
            self.rating = Decimal(rating[0])

        votes = self.trees[0].xpath(
            "//span[@class='ipl-rating-star__total-votes']/text()"
        )
        if votes and votes[0]:
            self.votes = int(votes[0].strip("()").replace(",", ""))

        rows = self.trees[0].xpath(
            "//table[@class='titlereference-list ipl-zebra-list']//tr"
        )
        for row in rows:
            key, value = row.xpath("./td")
            key = str(key.text)

            if key == "Genres":
                self.genres = [
                    x.text for x in value.xpath(".//a") if "/genre/" in x.attrib["href"]
                ]
            elif key == "Taglines":
                self.tagline = value.text.strip()
            elif key == "Plot Summary":
                plot = value.xpath("./p")
                if plot:
                    self.plot = plot[0].text.strip()
            elif key == "Plot Keywords":
                self.plot_keywords = [
                    x.text
                    for x in value.xpath(".//a")
                    if "/keyword/" in x.attrib["href"]
                ]
            elif key == "Also Known As":
                self.alternative_titles += [
                    x.strip().split("\n")[0].strip()
                    for x in value.xpath(".//li/text()")
                    if x.strip()
                ]
            elif key == "Runtime":
                runtimes = re.findall("(\d+) min", " ".join(value.xpath(".//text()")))
                if runtimes:
                    self.duration = int(runtimes[0])
            elif key == "Country":
                self.countries = [
                    x.text
                    for x in value.xpath(".//a")
                    if "/country/" in x.attrib["href"]
                ]
            elif key == "Language":
                self.languages = [
                    x.text
                    for x in value.xpath(".//a")
                    if "/language/" in x.attrib["href"]
                ]

        summary_texts = self.trees[1].xpath("//div[@class='summary_text']/text()")
        if summary_texts:
            self.description = summary_texts[0].strip()

        storylines = self.trees[1].xpath(
            "//h2[text()='Storyline']/../div/p/span//text()"
        )
        if storylines:
            self.storyline = "".join(storylines).strip()
            if self.storyline.startswith("Add a Plot"):
                self.storyline = None

        release_dates = [
            x.strip()
            for x in self.trees[1].xpath("//h4[text()='Release Date:']/../text()")
            if x.strip()
        ]
        if release_dates:
            self.release_date = release_dates[0]

        rows = self.trees[0].xpath("//div[@class='titlereference-overview-section']")
        for row in rows:
            key = row.xpath("./text()")[0].strip()
            if (
                key == "Director:"
                or key == "Directors:"
                or key == "Writers:"
                or key == "Writer:"
            ):
                for elem in row.xpath(".//a"):
                    if "/name/" not in elem.attrib["href"]:
                        continue
                    p = Person(
                        re.findall("/nm(\d+)", elem.attrib["href"])[0], self.imdb
                    )
                    p.name = elem.text
                    if key == "Director:" or key == "Directors:":
                        self.directors.append(p)
                    elif key == "Writers:" or key == "Writer:":
                        self.writers.append(p)

        for row in self.trees[0].xpath(
            "//h4[@id='cast']/../../following-sibling::table[1]//tr//td[@itemprop='actor']"
        ):
            elem = row.xpath(".//a")
            if not elem:
                continue

            elem = elem[0]
            if "/name/" not in elem.attrib["href"]:
                continue

            p = Person(re.findall("/nm(\d+)", elem.attrib["href"])[0], self.imdb)
            p.name = elem.xpath("./span/text()")[0]
            self.actors.append(p)

        self.alternative_titles = list(set(self.alternative_titles))

        for rec_details in self.trees[1].xpath("//div[@class='rec_details']"):
            self.more_like_this.append(self.parse_recommendation(rec_details))

    def parse_recommendation(self, tree):
        tree_title = tree.xpath(".//div[@class='rec-title']")[0]
        imdb_id = tree_title.xpath("./a/@href")[0].split("/")[2][2:]
        movie = Movie(imdb_id, self.imdb)

        title = tree_title.xpath(".//a//text()")
        if title:
            movie.title = title[0].strip()

        year = tree_title.xpath("./span/text()")
        if year:
            try:
                movie.year = int(tree_title.xpath("./span/text()")[0].strip("()"))
            except ValueError:
                pass

        movie.genres = [
            x.strip()
            for x in tree.xpath(".//div[contains(@class, 'rec-cert-genre')]/text()")
            if x.strip()
        ]

        ratings = tree.xpath(".//div[contains(@class, 'rating-list')]/@title")
        if ratings:
            ratings = re.findall(r"([\d.]+)/10 \(([\d,]+) votes\)", ratings[0])
            if ratings:
                ratings = ratings[0]
                movie.rating = Decimal(ratings[0])
                movie.votes = int(ratings[1].replace(",", ""))

        movie.tagline = "".join(
            tree.xpath(".//div[@class='rec-outline']/p/text()")
        ).strip()

        return movie

    def __repr__(self):
        return "<Movie fetched=%r imdb_id=%r title=%r year=%r>" % (
            self.fetched,
            self.imdb_id,
            self.title,
            self.year,
        )

    def get_titles(self):
        yield self.title
        for title in self.alternative_titles:
            yield title
