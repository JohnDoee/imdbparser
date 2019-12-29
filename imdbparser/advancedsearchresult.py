import re
import sys
from decimal import Decimal

from requests.compat import quote_plus, urlencode

from .base import Base
from .movie import Movie
from .person import Person


class Option:
    def __init__(self, label, value):
        self.label = label.strip()
        self.value = value.strip()

    def __str__(self):
        return f"{self.label} ({self.value})"

    def __repr__(self):
        return f"Option({self.label!r}, {self.value!r})"


class ParseBase(Base):
    base_url = "https://www.imdb.com/search/title/?"

    def _get_urls(self):
        return [self.base_url + urlencode(self.query)]

    def parse(self, htmls):
        super().parse(htmls)

        self.results = []

        for row in self.trees[0].xpath(
            "//div[@class='lister-list']/div[contains(@class, 'lister-item')]"
        ):
            cover = row.xpath(".//img")[0]
            imdb_id = cover.attrib["data-tconst"]
            movie = Movie(imdb_id, self.imdb)
            movie.directors = []
            movie.actors = []
            cover = cover.attrib["src"]
            if "nopicture" not in cover:
                movie.cover = self.cleanup_photo_url(cover)

            header = row.xpath(".//h3[@class='lister-item-header']")[0]
            movie.title = header.xpath(".//a/text()")[0]
            year = re.findall(
                "\d+",
                header.xpath(".//span[contains(@class, 'lister-item-year')]/text()")[0],
            )
            if year and len(year[0]) == 4:
                movie.year = int(year[0])

            runtime = row.xpath(".//span[@class='runtime']")
            if runtime:
                runtime = re.findall("\d+", runtime[0].text)
                if runtime:
                    movie.duration = int(runtime[0])

            genres = row.xpath(".//span[@class='genre']")
            if genres:
                movie.genres = genres[0].text.split(", ")

            rating = row.xpath(".//div[contains(@class, 'ratings-imdb-rating')]")
            if rating:
                movie.rating = Decimal(rating[0].attrib["data-value"])

            votes = row.xpath(".//span[@class='sort-num_votes-visible']/span[2]")
            if votes:
                movie.votes = int(votes[0].attrib["data-value"])

            content = row.xpath("div[@class='lister-item-content']")[0]
            storyline = content.xpath("./p[2]")
            if storyline:
                movie.storyline = storyline[0].text.strip()

            people = content.xpath("./p[3]")
            if people:
                people = people[0]
                people_titles = iter(
                    [
                        t.strip(" ,\n:s")
                        for t in people.xpath("./text()")
                        if t.strip(" ,\n")
                    ]
                )
                current_title = next(people_titles)
                for e in people:
                    if e.tag == "span":
                        current_title = next(people_titles)
                    else:
                        p = Person(
                            re.findall("/nm(\d+)", e.attrib["href"])[0], self.imdb
                        )
                        p.name = e.text
                        if current_title == "Director":
                            movie.directors.append(p)
                        elif current_title == "Star":
                            movie.actors.append(p)

            self.results.append(movie)


class AS:
    class TITLE_TYPE:
        FEATURE_FILM = Option("Feature Film", "feature")
        TV_MOVIE = Option("TV Movie", "tv_movie")
        TV_SERIES = Option("TV Series", "tv_series")
        TV_EPISODE = Option("TV Episode", "tv_episode")
        TV_SPECIAL = Option("TV Special", "tv_special")
        MINI_SERIES = Option("Mini-Series", "tv_miniseries")
        DOCUMENTARY = Option("Documentary", "documentary")
        VIDEO_GAME = Option("Video Game", "video_game")
        SHORT_FILM = Option("Short Film", "short")
        VIDEO = Option("Video", "video")
        TV_SHORT = Option("TV Short", "tv_short")

    class GENRES:
        ACTION = Option("Action", "action")
        ADVENTURE = Option("Adventure", "adventure")
        ANIMATION = Option("Animation", "animation")
        BIOGRAPHY = Option("Biography", "biography")
        COMEDY = Option("Comedy", "comedy")
        CRIME = Option("Crime", "crime")
        DOCUMENTARY = Option("Documentary", "documentary")
        DRAMA = Option("Drama", "drama")
        FAMILY = Option("Family", "family")
        FANTASY = Option("Fantasy", "fantasy")
        FILM_NOIR = Option("Film-Noir", "film_noir")
        GAME_SHOW = Option("Game-Show", "game_show")
        HISTORY = Option("History", "history")
        HORROR = Option("Horror", "horror")
        MUSIC = Option("Music", "music")
        MUSICAL = Option("Musical", "musical")
        MYSTERY = Option("Mystery", "mystery")
        NEWS = Option("News", "news")
        REALITY_TV = Option("Reality-TV", "reality_tv")
        ROMANCE = Option("Romance", "romance")
        SCI_FI = Option("Sci-Fi", "sci_fi")
        SPORT = Option("Sport", "sport")
        TALK_SHOW = Option("Talk-Show", "talk_show")
        THRILLER = Option("Thriller", "thriller")
        WAR = Option("War", "war")
        WESTERN = Option("Western", "western")

    class GROUPS:
        IMDB_TOP_100 = Option('IMDb "Top 100"', "top_100")
        IMDB_TOP_250 = Option('IMDb "Top 250"', "top_250")
        IMDB_TOP_1000 = Option('IMDb "Top 1000"', "top_1000")
        OSCAR_WINNING = Option("Oscar-Winning", "oscar_winners")
        EMMY_AWARD_WINNING = Option("Emmy Award-Winning", "emmy_winners")
        GOLDEN_GLOBE_WINNING = Option("Golden Globe-Winning", "golden_globe_winners")
        OSCAR_NOMINATED = Option("Oscar-Nominated", "oscar_nominees")
        EMMY_AWARD_NOMINATED = Option("Emmy Award-Nominated", "emmy_nominees")
        GOLDEN_GLOBE_NOMINATED = Option(
            "Golden Globe-Nominated", "golden_globe_nominees"
        )
        BEST_PICTURE_WINNING = Option(
            "Best Picture-Winning", "oscar_best_picture_winners"
        )
        BEST_DIRECTOR_WINNING = Option(
            "Best Director-Winning", "oscar_best_director_winners"
        )
        NOW_PLAYING = Option("Now-Playing", "now-playing-us")
        BEST_PICTURE_NOMINATED = Option(
            "Best Picture-Nominated", "oscar_best_picture_nominees"
        )
        BEST_DIRECTOR_NOMINATED = Option(
            "Best Director-Nominated", "oscar_best_director_nominees"
        )
        NATIONAL_FILM_BOARD_PRESERVED = Option(
            "National Film Board Preserved", "national_film_registry"
        )
        RAZZIE_WINNING = Option("Razzie-Winning", "razzie_winners")
        IMDB_BOTTOM_100 = Option('IMDb "Bottom 100"', "bottom_100")
        IMDB_BOTTOM_250 = Option('IMDb "Bottom 250"', "bottom_250")
        RAZZIE_NOMINATED = Option("Razzie-Nominated", "razzie_nominees")
        IMDB_BOTTOM_1000 = Option('IMDb "Bottom 1000"', "bottom_1000")

    class HAS:
        ALTERNATE_VERSIONS = Option("Alternate Versions", "alternate-versions")
        AWARDS = Option("Awards", "awards")
        BUSINESS_INFO = Option("Business Info", "business-info")
        CRAZY_CREDITS = Option("Crazy Credits", "crazy-credits")
        GOOFS = Option("Goofs", "goofs")
        LOCATIONS = Option("Locations", "locations")
        PLOT = Option("Plot", "plot")
        QUOTES = Option("Quotes", "quotes")
        SOUNDTRACKS = Option("Soundtracks", "soundtracks")
        TECHNICAL_INFO = Option("Technical Info", "technical")
        TRIVIA = Option("Trivia", "trivia")
        X_RAY = Option("X-Ray", "x-ray")

    class COMPANIES:
        TWENTIETH_CENTURY_FOX = Option("20th Century Fox", "fox")
        SONY = Option("Sony", "columbia")
        DREAMWORKS = Option("DreamWorks", "dreamworks")
        MGM = Option("MGM", "mgm")
        PARAMOUNT = Option("Paramount", "paramount")
        UNIVERSAL = Option("Universal", "universal")
        WALT_DISNEY = Option("Walt Disney", "disney")
        WARNER_BROS = Option("Warner Bros.", "warner")

    class CERTIFICATES:
        G = Option("G", "us:G")
        PG = Option("PG", "us:PG")
        PG_13 = Option("PG-13", "us:PG-13")
        R = Option("R", "us:R")
        NC_17 = Option("NC-17", "us:NC-17")

    class COLORS:
        COLOR = Option("Color", "color")
        BLACK_WHITE = Option("Black & White", "black_and_white")
        COLORIZED = Option("Colorized", "colorized")
        ACES = Option("ACES", "aces")

    class COUNTRIES:
        AFGHANISTAN = Option("Afghanistan", "af")
        LAND_ISLANDS = Option("Åland Islands", "ax")
        ALBANIA = Option("Albania", "al")
        ALGERIA = Option("Algeria", "dz")
        AMERICAN_SAMOA = Option("American Samoa", "as")
        ANDORRA = Option("Andorra", "ad")
        ANGOLA = Option("Angola", "ao")
        ANGUILLA = Option("Anguilla", "ai")
        ANTARCTICA = Option("Antarctica", "aq")
        ANTIGUA_AND_BARBUDA = Option("Antigua and Barbuda", "ag")
        ARGENTINA = Option("Argentina", "ar")
        ARMENIA = Option("Armenia", "am")
        ARUBA = Option("Aruba", "aw")
        AUSTRALIA = Option("Australia", "au")
        AUSTRIA = Option("Austria", "at")
        AZERBAIJAN = Option("Azerbaijan", "az")
        BAHAMAS = Option("Bahamas", "bs")
        BAHRAIN = Option("Bahrain", "bh")
        BANGLADESH = Option("Bangladesh", "bd")
        BARBADOS = Option("Barbados", "bb")
        BELARUS = Option("Belarus", "by")
        BELGIUM = Option("Belgium", "be")
        BELIZE = Option("Belize", "bz")
        BENIN = Option("Benin", "bj")
        BERMUDA = Option("Bermuda", "bm")
        BHUTAN = Option("Bhutan", "bt")
        BOLIVIA = Option("Bolivia", "bo")
        BONAIRE_SINT_EUSTATIUS_AND_SABA = Option(
            "Bonaire, Sint Eustatius and Saba", "bq"
        )
        BOSNIA_AND_HERZEGOVINA = Option("Bosnia and Herzegovina", "ba")
        BOTSWANA = Option("Botswana", "bw")
        BOUVET_ISLAND = Option("Bouvet Island", "bv")
        BRAZIL = Option("Brazil", "br")
        BRITISH_INDIAN_OCEAN_TERRITORY = Option("British Indian Ocean Territory", "io")
        BRITISH_VIRGIN_ISLANDS = Option("British Virgin Islands", "vg")
        BRUNEI_DARUSSALAM = Option("Brunei Darussalam", "bn")
        BULGARIA = Option("Bulgaria", "bg")
        BURKINA_FASO = Option("Burkina Faso", "bf")
        BURMA = Option("Burma", "bumm")
        BURUNDI = Option("Burundi", "bi")
        CAMBODIA = Option("Cambodia", "kh")
        CAMEROON = Option("Cameroon", "cm")
        CANADA = Option("Canada", "ca")
        CAPE_VERDE = Option("Cape Verde", "cv")
        CAYMAN_ISLANDS = Option("Cayman Islands", "ky")
        CENTRAL_AFRICAN_REPUBLIC = Option("Central African Republic", "cf")
        CHAD = Option("Chad", "td")
        CHILE = Option("Chile", "cl")
        CHINA = Option("China", "cn")
        CHRISTMAS_ISLAND = Option("Christmas Island", "cx")
        COCOS_KEELING_ISLANDS = Option("Cocos (Keeling) Islands", "cc")
        COLOMBIA = Option("Colombia", "co")
        COMOROS = Option("Comoros", "km")
        CONGO = Option("Congo", "cg")
        COOK_ISLANDS = Option("Cook Islands", "ck")
        COSTA_RICA = Option("Costa Rica", "cr")
        CTE_D_IVOIRE = Option("Côte d'Ivoire", "ci")
        CROATIA = Option("Croatia", "hr")
        CUBA = Option("Cuba", "cu")
        CYPRUS = Option("Cyprus", "cy")
        CZECH_REPUBLIC = Option("Czech Republic", "cz")
        CZECHOSLOVAKIA = Option("Czechoslovakia", "cshh")
        DEMOCRATIC_REPUBLIC_OF_THE_CONGO = Option(
            "Democratic Republic of the Congo", "cd"
        )
        DENMARK = Option("Denmark", "dk")
        DJIBOUTI = Option("Djibouti", "dj")
        DOMINICA = Option("Dominica", "dm")
        DOMINICAN_REPUBLIC = Option("Dominican Republic", "do")
        EAST_GERMANY = Option("East Germany", "ddde")
        ECUADOR = Option("Ecuador", "ec")
        EGYPT = Option("Egypt", "eg")
        EL_SALVADOR = Option("El Salvador", "sv")
        EQUATORIAL_GUINEA = Option("Equatorial Guinea", "gq")
        ERITREA = Option("Eritrea", "er")
        ESTONIA = Option("Estonia", "ee")
        ETHIOPIA = Option("Ethiopia", "et")
        FALKLAND_ISLANDS = Option("Falkland Islands", "fk")
        FAROE_ISLANDS = Option("Faroe Islands", "fo")
        FEDERAL_REPUBLIC_OF_YUGOSLAVIA = Option(
            "Federal Republic of Yugoslavia", "yucs"
        )
        FEDERATED_STATES_OF_MICRONESIA = Option("Federated States of Micronesia", "fm")
        FIJI = Option("Fiji", "fj")
        FINLAND = Option("Finland", "fi")
        FRANCE = Option("France", "fr")
        FRENCH_GUIANA = Option("French Guiana", "gf")
        FRENCH_POLYNESIA = Option("French Polynesia", "pf")
        FRENCH_SOUTHERN_TERRITORIES = Option("French Southern Territories", "tf")
        GABON = Option("Gabon", "ga")
        GAMBIA = Option("Gambia", "gm")
        GEORGIA = Option("Georgia", "ge")
        GERMANY = Option("Germany", "de")
        GHANA = Option("Ghana", "gh")
        GIBRALTAR = Option("Gibraltar", "gi")
        GREECE = Option("Greece", "gr")
        GREENLAND = Option("Greenland", "gl")
        GRENADA = Option("Grenada", "gd")
        GUADELOUPE = Option("Guadeloupe", "gp")
        GUAM = Option("Guam", "gu")
        GUATEMALA = Option("Guatemala", "gt")
        GUERNSEY = Option("Guernsey", "gg")
        GUINEA = Option("Guinea", "gn")
        GUINEA_BISSAU = Option("Guinea-Bissau", "gw")
        GUYANA = Option("Guyana", "gy")
        HAITI = Option("Haiti", "ht")
        HEARD_ISLAND_AND_MCDONALD_ISLANDS = Option(
            "Heard Island and McDonald Islands", "hm"
        )
        HOLY_SEE_VATICAN_CITY_STATE = Option("Holy See (Vatican City State)", "va")
        HONDURAS = Option("Honduras", "hn")
        HONG_KONG = Option("Hong Kong", "hk")
        HUNGARY = Option("Hungary", "hu")
        ICELAND = Option("Iceland", "is")
        INDIA = Option("India", "in")
        INDONESIA = Option("Indonesia", "id")
        IRAN = Option("Iran", "ir")
        IRAQ = Option("Iraq", "iq")
        IRELAND = Option("Ireland", "ie")
        ISLE_OF_MAN = Option("Isle of Man", "im")
        ISRAEL = Option("Israel", "il")
        ITALY = Option("Italy", "it")
        JAMAICA = Option("Jamaica", "jm")
        JAPAN = Option("Japan", "jp")
        JERSEY = Option("Jersey", "je")
        JORDAN = Option("Jordan", "jo")
        KAZAKHSTAN = Option("Kazakhstan", "kz")
        KENYA = Option("Kenya", "ke")
        KIRIBATI = Option("Kiribati", "ki")
        KOREA = Option("Korea", "xko")
        KOSOVO = Option("Kosovo", "xkv")
        KUWAIT = Option("Kuwait", "kw")
        KYRGYZSTAN = Option("Kyrgyzstan", "kg")
        LAOS = Option("Laos", "la")
        LATVIA = Option("Latvia", "lv")
        LEBANON = Option("Lebanon", "lb")
        LESOTHO = Option("Lesotho", "ls")
        LIBERIA = Option("Liberia", "lr")
        LIBYA = Option("Libya", "ly")
        LIECHTENSTEIN = Option("Liechtenstein", "li")
        LITHUANIA = Option("Lithuania", "lt")
        LUXEMBOURG = Option("Luxembourg", "lu")
        MACAO = Option("Macao", "mo")
        MADAGASCAR = Option("Madagascar", "mg")
        MALAWI = Option("Malawi", "mw")
        MALAYSIA = Option("Malaysia", "my")
        MALDIVES = Option("Maldives", "mv")
        MALI = Option("Mali", "ml")
        MALTA = Option("Malta", "mt")
        MARSHALL_ISLANDS = Option("Marshall Islands", "mh")
        MARTINIQUE = Option("Martinique", "mq")
        MAURITANIA = Option("Mauritania", "mr")
        MAURITIUS = Option("Mauritius", "mu")
        MAYOTTE = Option("Mayotte", "yt")
        MEXICO = Option("Mexico", "mx")
        MOLDOVA = Option("Moldova", "md")
        MONACO = Option("Monaco", "mc")
        MONGOLIA = Option("Mongolia", "mn")
        MONTENEGRO = Option("Montenegro", "me")
        MONTSERRAT = Option("Montserrat", "ms")
        MOROCCO = Option("Morocco", "ma")
        MOZAMBIQUE = Option("Mozambique", "mz")
        MYANMAR = Option("Myanmar", "mm")
        NAMIBIA = Option("Namibia", "na")
        NAURU = Option("Nauru", "nr")
        NEPAL = Option("Nepal", "np")
        NETHERLANDS = Option("Netherlands", "nl")
        NETHERLANDS_ANTILLES = Option("Netherlands Antilles", "an")
        NEW_CALEDONIA = Option("New Caledonia", "nc")
        NEW_ZEALAND = Option("New Zealand", "nz")
        NICARAGUA = Option("Nicaragua", "ni")
        NIGER = Option("Niger", "ne")
        NIGERIA = Option("Nigeria", "ng")
        NIUE = Option("Niue", "nu")
        NORFOLK_ISLAND = Option("Norfolk Island", "nf")
        NORTH_KOREA = Option("North Korea", "kp")
        NORTH_VIETNAM = Option("North Vietnam", "vdvn")
        NORTHERN_MARIANA_ISLANDS = Option("Northern Mariana Islands", "mp")
        NORWAY = Option("Norway", "no")
        OMAN = Option("Oman", "om")
        PAKISTAN = Option("Pakistan", "pk")
        PALAU = Option("Palau", "pw")
        PALESTINE = Option("Palestine", "xpi")
        PALESTINIAN_TERRITORY = Option("Palestinian Territory", "ps")
        PANAMA = Option("Panama", "pa")
        PAPUA_NEW_GUINEA = Option("Papua New Guinea", "pg")
        PARAGUAY = Option("Paraguay", "py")
        PERU = Option("Peru", "pe")
        PHILIPPINES = Option("Philippines", "ph")
        POLAND = Option("Poland", "pl")
        PORTUGAL = Option("Portugal", "pt")
        PITCAIRN = Option("Pitcairn", "pn")
        PUERTO_RICO = Option("Puerto Rico", "pr")
        QATAR = Option("Qatar", "qa")
        REPUBLIC_OF_MACEDONIA = Option("Republic of Macedonia", "mk")
        RUNION = Option("Réunion", "re")
        ROMANIA = Option("Romania", "ro")
        RUSSIA = Option("Russia", "ru")
        RWANDA = Option("Rwanda", "rw")
        SAINT_BARTHLEMY = Option("Saint Barthélemy", "bl")
        SAINT_HELENA = Option("Saint Helena", "sh")
        SAINT_KITTS_AND_NEVIS = Option("Saint Kitts and Nevis", "kn")
        SAINT_LUCIA = Option("Saint Lucia", "lc")
        SAINT_MARTIN_FRENCH_PART = Option("Saint Martin (French part)", "mf")
        SAINT_PIERRE_AND_MIQUELON = Option("Saint Pierre and Miquelon", "pm")
        SAINT_VINCENT_AND_THE_GRENADINES = Option(
            "Saint Vincent and the Grenadines", "vc"
        )
        SAMOA = Option("Samoa", "ws")
        SAN_MARINO = Option("San Marino", "sm")
        SAO_TOME_AND_PRINCIPE = Option("Sao Tome and Principe", "st")
        SAUDI_ARABIA = Option("Saudi Arabia", "sa")
        SENEGAL = Option("Senegal", "sn")
        SERBIA = Option("Serbia", "rs")
        SERBIA_AND_MONTENEGRO = Option("Serbia and Montenegro", "csxx")
        SEYCHELLES = Option("Seychelles", "sc")
        SIAM = Option("Siam", "xsi")
        SIERRA_LEONE = Option("Sierra Leone", "sl")
        SINGAPORE = Option("Singapore", "sg")
        SLOVAKIA = Option("Slovakia", "sk")
        SLOVENIA = Option("Slovenia", "si")
        SOLOMON_ISLANDS = Option("Solomon Islands", "sb")
        SOMALIA = Option("Somalia", "so")
        SOUTH_AFRICA = Option("South Africa", "za")
        SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = Option(
            "South Georgia and the South Sandwich Islands", "gs"
        )
        SOUTH_KOREA = Option("South Korea", "kr")
        SOVIET_UNION = Option("Soviet Union", "suhh")
        SPAIN = Option("Spain", "es")
        SRI_LANKA = Option("Sri Lanka", "lk")
        SUDAN = Option("Sudan", "sd")
        SURINAME = Option("Suriname", "sr")
        SVALBARD_AND_JAN_MAYEN = Option("Svalbard and Jan Mayen", "sj")
        SWAZILAND = Option("Swaziland", "sz")
        SWEDEN = Option("Sweden", "se")
        SWITZERLAND = Option("Switzerland", "ch")
        SYRIA = Option("Syria", "sy")
        TAIWAN = Option("Taiwan", "tw")
        TAJIKISTAN = Option("Tajikistan", "tj")
        TANZANIA = Option("Tanzania", "tz")
        THAILAND = Option("Thailand", "th")
        TIMOR_LESTE = Option("Timor-Leste", "tl")
        TOGO = Option("Togo", "tg")
        TOKELAU = Option("Tokelau", "tk")
        TONGA = Option("Tonga", "to")
        TRINIDAD_AND_TOBAGO = Option("Trinidad and Tobago", "tt")
        TUNISIA = Option("Tunisia", "tn")
        TURKEY = Option("Turkey", "tr")
        TURKMENISTAN = Option("Turkmenistan", "tm")
        TURKS_AND_CAICOS_ISLANDS = Option("Turks and Caicos Islands", "tc")
        TUVALU = Option("Tuvalu", "tv")
        U_S_VIRGIN_ISLANDS = Option("U.S. Virgin Islands", "vi")
        UGANDA = Option("Uganda", "ug")
        UKRAINE = Option("Ukraine", "ua")
        UNITED_ARAB_EMIRATES = Option("United Arab Emirates", "ae")
        UNITED_KINGDOM = Option("United Kingdom", "gb")
        UNITED_STATES = Option("United States", "us")
        UNITED_STATES_MINOR_OUTLYING_ISLANDS = Option(
            "United States Minor Outlying Islands", "um"
        )
        URUGUAY = Option("Uruguay", "uy")
        UZBEKISTAN = Option("Uzbekistan", "uz")
        VANUATU = Option("Vanuatu", "vu")
        VENEZUELA = Option("Venezuela", "ve")
        VIETNAM = Option("Vietnam", "vn")
        WALLIS_AND_FUTUNA = Option("Wallis and Futuna", "wf")
        WEST_GERMANY = Option("West Germany", "xwg")
        WESTERN_SAHARA = Option("Western Sahara", "eh")
        YEMEN = Option("Yemen", "ye")
        YUGOSLAVIA = Option("Yugoslavia", "xyu")
        ZAIRE = Option("Zaire", "zrcd")
        ZAMBIA = Option("Zambia", "zm")
        ZIMBABWE = Option("Zimbabwe", "zw")

    class LANGUAGES:
        ABKHAZIAN = Option("Abkhazian", "ab")
        ABORIGINAL = Option("Aboriginal", "qac")
        ACH = Option("Aché", "guq")
        ACHOLI = Option("Acholi", "qam")
        AFRIKAANS = Option("Afrikaans", "af")
        AIDOUKROU = Option("Aidoukrou", "qas")
        AKAN = Option("Akan", "ak")
        ALBANIAN = Option("Albanian", "sq")
        ALGONQUIN = Option("Algonquin", "alg")
        AMERICAN_SIGN_LANGUAGE = Option("American Sign Language", "ase")
        AMHARIC = Option("Amharic", "am")
        APACHE_LANGUAGES = Option("Apache languages", "apa")
        ARABIC = Option("Arabic", "ar")
        ARAGONESE = Option("Aragonese", "an")
        ARAMAIC = Option("Aramaic", "arc")
        ARAPAHO = Option("Arapaho", "arp")
        ARMENIAN = Option("Armenian", "hy")
        ASSAMESE = Option("Assamese", "as")
        ASSYRIAN_NEO_ARAMAIC = Option("Assyrian Neo-Aramaic", "aii")
        ATHAPASCAN_LANGUAGES = Option("Athapascan languages", "ath")
        AUSTRALIAN_SIGN_LANGUAGE = Option("Australian Sign Language", "asf")
        AWADHI = Option("Awadhi", "awa")
        AYMARA = Option("Aymara", "ay")
        AZERBAIJANI = Option("Azerbaijani", "az")
        BABLE = Option("Bable", "ast")
        BAKA = Option("Baka", "qbd")
        BALINESE = Option("Balinese", "ban")
        BAMBARA = Option("Bambara", "bm")
        BASQUE = Option("Basque", "eu")
        BASSARI = Option("Bassari", "bsc")
        BELARUSIAN = Option("Belarusian", "be")
        BEMBA = Option("Bemba", "bem")
        BENGALI = Option("Bengali", "bn")
        BERBER_LANGUAGES = Option("Berber languages", "ber")
        BHOJPURI = Option("Bhojpuri", "bho")
        BICOLANO = Option("Bicolano", "qbi")
        BODO = Option("Bodo", "qbh")
        BOSNIAN = Option("Bosnian", "bs")
        BRAZILIAN_SIGN_LANGUAGE = Option("Brazilian Sign Language", "bzs")
        BRETON = Option("Breton", "br")
        BRITISH_SIGN_LANGUAGE = Option("British Sign Language", "bfi")
        BULGARIAN = Option("Bulgarian", "bg")
        BURMESE = Option("Burmese", "my")
        CANTONESE = Option("Cantonese", "yue")
        CATALAN = Option("Catalan", "ca")
        CENTRAL_KHMER = Option("Central Khmer", "km")
        CHAKMA = Option("Chakma", "ccp")
        CHAOZHOU = Option("Chaozhou", "qax")
        CHECHEN = Option("Chechen", "ce")
        CHEROKEE = Option("Cherokee", "chr")
        CHEYENNE = Option("Cheyenne", "chy")
        CHHATTISGARHI = Option("Chhattisgarhi", "hne")
        CHINESE = Option("Chinese", "zh")
        CORNISH = Option("Cornish", "kw")
        CORSICAN = Option("Corsican", "co")
        CREE = Option("Cree", "cr")
        CREEK = Option("Creek", "mus")
        CROATIAN = Option("Croatian", "hr")
        CROW = Option("Crow", "cro")
        CZECH = Option("Czech", "cs")
        DANISH = Option("Danish", "da")
        DARI = Option("Dari", "prs")
        DESIYA = Option("Desiya", "dso")
        DINKA = Option("Dinka", "din")
        DJERMA = Option("Djerma", "qaw")
        DOGRI = Option("Dogri", "doi")
        DUTCH = Option("Dutch", "nl")
        DYULA = Option("Dyula", "dyu")
        DZONGKHA = Option("Dzongkha", "dz")
        EAST_GREENLANDIC = Option("East-Greenlandic", "qbc")
        EASTERN_FRISIAN = Option("Eastern Frisian", "frs")
        EGYPTIAN_ANCIENT = Option("Egyptian (Ancient)", "egy")
        ENGLISH = Option("English", "en")
        ESPERANTO = Option("Esperanto", "eo")
        ESTONIAN = Option("Estonian", "et")
        EWE = Option("Ewe", "ee")
        FALIASCH = Option("Faliasch", "qbg")
        FAROESE = Option("Faroese", "fo")
        FILIPINO = Option("Filipino", "fil")
        FINNISH = Option("Finnish", "fi")
        FLEMISH = Option("Flemish", "qbn")
        FON = Option("Fon", "fon")
        FRENCH = Option("French", "fr")
        FRENCH_SIGN_LANGUAGE = Option("French Sign Language", "fsl")
        FULAH = Option("Fulah", "ff")
        FUR = Option("Fur", "fvr")
        GAELIC = Option("Gaelic", "gd")
        GALICIAN = Option("Galician", "gl")
        GEORGIAN = Option("Georgian", "ka")
        GERMAN = Option("German", "de")
        GERMAN_SIGN_LANGUAGE = Option("German Sign Language", "gsg")
        GREBO = Option("Grebo", "grb")
        GREEK = Option("Greek", "el")
        GREEK_ANCIENT_TO_1453 = Option("Greek, Ancient (to 1453)", "grc")
        GREENLANDIC = Option("Greenlandic", "kl")
        GUARANI = Option("Guarani", "gn")
        GUJARATI = Option("Gujarati", "gu")
        GUMATJ = Option("Gumatj", "gnn")
        GUNWINGGU = Option("Gunwinggu", "gup")
        HAITIAN = Option("Haitian", "ht")
        HAIDA = Option("Haida", "hai")
        HAKKA = Option("Hakka", "hak")
        HARYANVI = Option("Haryanvi", "bgc")
        HASSANYA = Option("Hassanya", "qav")
        HAUSA = Option("Hausa", "ha")
        HAWAIIAN = Option("Hawaiian", "haw")
        HEBREW = Option("Hebrew", "he")
        HINDI = Option("Hindi", "hi")
        HMONG = Option("Hmong", "hmn")
        HOKKIEN = Option("Hokkien", "qab")
        HOPI = Option("Hopi", "hop")
        HUNGARIAN = Option("Hungarian", "hu")
        IBAN = Option("Iban", "iba")
        IBO = Option("Ibo", "qag")
        ICELANDIC = Option("Icelandic", "is")
        ICELANDIC_SIGN_LANGUAGE = Option("Icelandic Sign Language", "icl")
        INDIAN_SIGN_LANGUAGE = Option("Indian Sign Language", "ins")
        INDONESIAN = Option("Indonesian", "id")
        INUKTITUT = Option("Inuktitut", "iu")
        INUPIAQ = Option("Inupiaq", "ik")
        IRISH_GAELIC = Option("Irish Gaelic", "ga")
        IRULA = Option("Irula", "iru")
        ITALIAN = Option("Italian", "it")
        JAPANESE = Option("Japanese", "ja")
        JAPANESE_SIGN_LANGUAGE = Option("Japanese Sign Language", "jsl")
        JOLA_FONYI = Option("Jola-Fonyi", "dyo")
        JU_HOAN = Option("Ju'hoan", "ktz")
        KAADO = Option("Kaado", "qbf")
        KABUVERDIANU = Option("Kabuverdianu", "kea")
        KABYLE = Option("Kabyle", "kab")
        KALMYK_OIRAT = Option("Kalmyk-Oirat", "xal")
        KANNADA = Option("Kannada", "kn")
        KARAJ = Option("Karajá", "kpj")
        KARBI = Option("Karbi", "mjw")
        KAREN = Option("Karen", "kar")
        KAZAKH = Option("Kazakh", "kk")
        KHANTY = Option("Khanty", "kca")
        KHASI = Option("Khasi", "kha")
        KIKUYU = Option("Kikuyu", "ki")
        KINYARWANDA = Option("Kinyarwanda", "rw")
        KIRUNDI = Option("Kirundi", "qar")
        KLINGON = Option("Klingon", "tlh")
        KODAVA = Option("Kodava", "kfa")
        KONKANI = Option("Konkani", "kok")
        KOREAN = Option("Korean", "ko")
        KOREAN_SIGN_LANGUAGE = Option("Korean Sign Language", "kvk")
        KOROWAI = Option("Korowai", "khe")
        KRIOLU = Option("Kriolu", "qaq")
        KRU = Option("Kru", "kro")
        KUDMALI = Option("Kudmali", "kyw")
        KUNA = Option("Kuna", "qbb")
        KURDISH = Option("Kurdish", "ku")
        KWAKIUTL = Option("Kwakiutl", "kwk")
        KYRGYZ = Option("Kyrgyz", "ky")
        LADAKHI = Option("Ladakhi", "lbj")
        LADINO = Option("Ladino", "lad")
        LAO = Option("Lao", "lo")
        LATIN = Option("Latin", "la")
        LATVIAN = Option("Latvian", "lv")
        LIMBU = Option("Limbu", "lif")
        LINGALA = Option("Lingala", "ln")
        LITHUANIAN = Option("Lithuanian", "lt")
        LOW_GERMAN = Option("Low German", "nds")
        LUXEMBOURGISH = Option("Luxembourgish", "lb")
        MACEDONIAN = Option("Macedonian", "mk")
        MACRO_J = Option("Macro-Jê", "qbm")
        MAGAHI = Option("Magahi", "mag")
        MAITHILI = Option("Maithili", "mai")
        MALAGASY = Option("Malagasy", "mg")
        MALAY = Option("Malay", "ms")
        MALAYALAM = Option("Malayalam", "ml")
        MALECITE_PASSAMAQUODDY = Option("Malecite-Passamaquoddy", "pqm")
        MALINKA = Option("Malinka", "qap")
        MALTESE = Option("Maltese", "mt")
        MANCHU = Option("Manchu", "mnc")
        MANDARIN = Option("Mandarin", "cmn")
        MANDINGO = Option("Mandingo", "man")
        MANIPURI = Option("Manipuri", "mni")
        MAORI = Option("Maori", "mi")
        MAPUDUNGUN = Option("Mapudungun", "arn")
        MARATHI = Option("Marathi", "mr")
        MARSHALLESE = Option("Marshallese", "mh")
        MASAI = Option("Masai", "mas")
        MASALIT = Option("Masalit", "mls")
        MAYA = Option("Maya", "myn")
        MENDE = Option("Mende", "men")
        MICMAC = Option("Micmac", "mic")
        MIDDLE_ENGLISH = Option("Middle English", "enm")
        MIN_NAN = Option("Min Nan", "nan")
        MINANGKABAU = Option("Minangkabau", "min")
        MIRANDESE = Option("Mirandese", "mwl")
        MIXTEC = Option("Mixtec", "qmt")
        MIZO = Option("Mizo", "lus")
        MOHAWK = Option("Mohawk", "moh")
        MONGOLIAN = Option("Mongolian", "mn")
        MONTAGNAIS = Option("Montagnais", "moe")
        MORE = Option("More", "qaf")
        MORISYEN = Option("Morisyen", "mfe")
        NAGPURI = Option("Nagpuri", "qbl")
        NAHUATL = Option("Nahuatl", "nah")
        NAMA = Option("Nama", "qba")
        NAVAJO = Option("Navajo", "nv")
        NAXI = Option("Naxi", "nbf")
        NDEBELE = Option("Ndebele", "nd")
        NEAPOLITAN = Option("Neapolitan", "nap")
        NENETS = Option("Nenets", "yrk")
        NEPALI = Option("Nepali", "ne")
        NISGA_A = Option("Nisga'a", "ncg")
        NONE = Option("None", "zxx")
        NORSE_OLD = Option("Norse, Old", "non")
        NORTH_AMERICAN_INDIAN = Option("North American Indian", "nai")
        NORWEGIAN = Option("Norwegian", "no")
        NUSHI = Option("Nushi", "qbk")
        NYANEKA = Option("Nyaneka", "nyk")
        NYANJA = Option("Nyanja", "ny")
        OCCITAN = Option("Occitan", "oc")
        OJIBWA = Option("Ojibwa", "oj")
        OJIHIMBA = Option("Ojihimba", "qaz")
        OLD_ENGLISH = Option("Old English", "ang")
        ORIYA = Option("Oriya", "or")
        PAPIAMENTO = Option("Papiamento", "pap")
        PARSEE = Option("Parsee", "qaj")
        PASHTU = Option("Pashtu", "ps")
        PAWNEE = Option("Pawnee", "paw")
        PERSIAN = Option("Persian", "fa")
        PEUL = Option("Peul", "qai")
        POLISH = Option("Polish", "pl")
        POLYNESIAN = Option("Polynesian", "qah")
        PORTUGUESE = Option("Portuguese", "pt")
        PULAR = Option("Pular", "fuf")
        PUNJABI = Option("Punjabi", "pa")
        PUREPECHA = Option("Purepecha", "tsz")
        QUECHUA = Option("Quechua", "qu")
        QUENYA = Option("Quenya", "qya")
        RAJASTHANI = Option("Rajasthani", "raj")
        RAWAN = Option("Rawan", "qbj")
        RHAETIAN = Option("Rhaetian", "xrr")
        ROMANIAN = Option("Romanian", "ro")
        ROMANSH = Option("Romansh", "rm")
        ROMANY = Option("Romany", "rom")
        ROTUMAN = Option("Rotuman", "rtm")
        RUSSIAN = Option("Russian", "ru")
        RUSSIAN_SIGN_LANGUAGE = Option("Russian Sign Language", "rsl")
        RYUKYUAN = Option("Ryukyuan", "qao")
        SAAMI = Option("Saami", "qae")
        SAMOAN = Option("Samoan", "sm")
        SANSKRIT = Option("Sanskrit", "sa")
        SARDINIAN = Option("Sardinian", "sc")
        SCANIAN = Option("Scanian", "qay")
        SERBIAN = Option("Serbian", "sr")
        SERBO_CROATIAN = Option("Serbo-Croatian", "qbo")
        SERER = Option("Serer", "srr")
        SHANGHAINESE = Option("Shanghainese", "qad")
        SHANXI = Option("Shanxi", "qau")
        SHONA = Option("Shona", "sn")
        SHOSHONI = Option("Shoshoni", "shh")
        SICILIAN = Option("Sicilian", "scn")
        SINDARIN = Option("Sindarin", "sjn")
        SINDHI = Option("Sindhi", "sd")
        SINHALA = Option("Sinhala", "si")
        SIOUX = Option("Sioux", "sio")
        SLOVAK = Option("Slovak", "sk")
        SLOVENIAN = Option("Slovenian", "sl")
        SOMALI = Option("Somali", "so")
        SONGHAY = Option("Songhay", "son")
        SONINKE = Option("Soninke", "snk")
        SORBIAN_LANGUAGES = Option("Sorbian languages", "wen")
        SOTHO = Option("Sotho", "st")
        SOUSSON = Option("Sousson", "qbe")
        SPANISH = Option("Spanish", "es")
        SPANISH_SIGN_LANGUAGE = Option("Spanish Sign Language", "ssp")
        SRANAN = Option("Sranan", "srn")
        SWAHILI = Option("Swahili", "sw")
        SWEDISH = Option("Swedish", "sv")
        SWISS_GERMAN = Option("Swiss German", "gsw")
        SYLHETI = Option("Sylheti", "syl")
        TAGALOG = Option("Tagalog", "tl")
        TAJIK = Option("Tajik", "tg")
        TAMASHEK = Option("Tamashek", "tmh")
        TAMIL = Option("Tamil", "ta")
        TARAHUMARA = Option("Tarahumara", "tac")
        TATAR = Option("Tatar", "tt")
        TELUGU = Option("Telugu", "te")
        TEOCHEW = Option("Teochew", "qak")
        THAI = Option("Thai", "th")
        TIBETAN = Option("Tibetan", "bo")
        TIGRIGNA = Option("Tigrigna", "qan")
        TLINGIT = Option("Tlingit", "tli")
        TOK_PISIN = Option("Tok Pisin", "tpi")
        TONGA_TONGA_ISLANDS = Option("Tonga (Tonga Islands)", "to")
        TSONGA = Option("Tsonga", "ts")
        TSWA = Option("Tswa", "tsc")
        TSWANA = Option("Tswana", "tn")
        TULU = Option("Tulu", "tcy")
        TUPI = Option("Tupi", "tup")
        TURKISH = Option("Turkish", "tr")
        TURKMEN = Option("Turkmen", "tk")
        TUVINIAN = Option("Tuvinian", "tyv")
        TZOTZIL = Option("Tzotzil", "tzo")
        UKRAINIAN = Option("Ukrainian", "uk")
        UKRAINIAN_SIGN_LANGUAGE = Option("Ukrainian Sign Language", "ukl")
        UNGWATSI = Option("Ungwatsi", "qat")
        URDU = Option("Urdu", "ur")
        UZBEK = Option("Uzbek", "uz")
        VIETNAMESE = Option("Vietnamese", "vi")
        VISAYAN = Option("Visayan", "qaa")
        WASHOE = Option("Washoe", "was")
        WELSH = Option("Welsh", "cy")
        WOLOF = Option("Wolof", "wo")
        XHOSA = Option("Xhosa", "xh")
        YAKUT = Option("Yakut", "sah")
        YAPESE = Option("Yapese", "yap")
        YIDDISH = Option("Yiddish", "yi")
        YORUBA = Option("Yoruba", "yo")
        ZULU = Option("Zulu", "zu")

    class SOUND_MIXES:
        MONO = Option("Mono", "mono")
        SILENT = Option("Silent", "silent")
        STEREO = Option("Stereo", "stereo")
        DOLBY_DIGITAL = Option("Dolby Digital", "dolby_digital")
        DOLBY = Option("Dolby", "dolby")
        DOLBY_SR = Option("Dolby SR", "dolby_sr")
        DTS = Option("DTS", "dts")
        SDDS = Option("SDDS", "sdds")
        ULTRA_STEREO = Option("Ultra Stereo", "ultra_stereo")
        _TRACK_STEREO = Option("6-Track Stereo", "6_track_stereo")
        _MM_6_TRACK = Option("70 mm 6-Track", "70_mm_6_track")
        VITAPHONE = Option("Vitaphone", "vitaphone")
        DOLBY_DIGITAL_EX = Option("Dolby Digital EX", "dolby_digital_ex")
        DE_FOREST_PHONOFILM = Option("De Forest Phonofilm", "de_forest_phonofilm")
        DTS_STEREO = Option("DTS-Stereo", "dts_stereo")
        CHRONOPHONE = Option("Chronophone", "chronophone")
        DTS_ES = Option("DTS-ES", "dts_es")
        PERSPECTA_STEREO = Option("Perspecta Stereo", "perspecta_stereo")
        CINEPHONE = Option("Cinephone", "cinephone")
        _CHANNEL_STEREO = Option("3 Channel Stereo", "3_channel_stereo")
        CINEMATOPHONE = Option("Cinematophone", "cinematophone")
        SONICS_DDP = Option("Sonics-DDP", "sonics_ddp")
        _TRACK_DIGITAL_SOUND = Option(
            "12-Track Digital Sound", "12_track_digital_sound"
        )
        DTS_70_MM = Option("DTS 70 mm", "dts_70_mm")
        IMAX_6_TRACK = Option("IMAX 6-Track", "imax_6_track")
        MATRIX_SURROUND = Option("Matrix Surround", "matrix_surround")
        SONIX = Option("Sonix", "sonix")
        SENSURROUND = Option("Sensurround", "sensurround")
        CINERAMA_7_TRACK = Option("Cinerama 7-Track", "cinerama_7_track")
        KINOPLASTICON = Option("Kinoplasticon", "kinoplasticon")
        DIGITRAC_DIGITAL_AUDIO_SYSTEM = Option(
            "Digitrac Digital Audio System", "digitrac_digital_audio_system"
        )
        CINESOUND = Option("Cinesound", "cinesound")
        PHONO_KINEMA = Option("Phono-Kinema", "phono_kinema")
        CDS = Option("CDS", "cds")
        LC_CONCEPT_DIGITAL_SOUND = Option(
            "LC-Concept Digital Sound", "lc_concept_digital_sound"
        )

    class MY_RATINGS:
        INCLUDE_ALL_TITLES = Option("Include All Titles", "")
        EXCLUDE_TITLES_I_VE_SEEN = Option("Exclude Titles I've Seen", "exclude")
        RESTRICT_TO_TITLES_I_VE_SEEN = Option(
            "Restrict to Titles I've Seen", "restrict"
        )

    class NOW_PLAYING:
        SHOW_ALL_TITLES = Option("Show All Titles", "")
        ONLY_SHOW_TITLES_CURRENTLY_PLAYING_NEAR_ME = Option(
            "Only Show Titles Currently Playing Near Me", "restrict"
        )

    class ADULT:
        EXCLUDE = Option("Exclude", "")
        INCLUDE = Option("Include", "include")


class AdvancedSearchResult(ParseBase):
    def __init__(
        self,
        imdb,
        title="",
        title_type=[],
        release_date=("", ""),
        user_rating=("", ""),
        num_votes=("", ""),
        genres=[],
        groups=[],
        has=[],
        companies=[],
        certificates=[],
        colors=[],
        countries=[],
        keywords="",
        languages=[],
        locations="",
        moviemeter=("", ""),
        plot="",
        runtime=("", ""),
        sound_mixes=[],
        my_ratings=[],
        now_playing=[],
        adult=[],
    ):
        self.imdb = imdb

        self.query = {}
        self.query["title"] = title
        self.query["title_type"] = ",".join(
            [isinstance(v, str) and v or v.value for v in title_type]
        )
        self.query["release_date-min"] = release_date[0]
        self.query["release_date-max"] = release_date[1]
        self.query["user_rating-min"] = user_rating[0]
        self.query["user_rating-max"] = user_rating[1]
        self.query["num_votes-min"] = num_votes[0]
        self.query["num_votes-max"] = num_votes[1]
        self.query["genres"] = ",".join(
            [isinstance(v, str) and v or v.value for v in genres]
        )
        self.query["groups"] = ",".join(
            [isinstance(v, str) and v or v.value for v in groups]
        )
        self.query["has"] = ",".join([isinstance(v, str) and v or v.value for v in has])
        self.query["companies"] = ",".join(
            [isinstance(v, str) and v or v.value for v in companies]
        )
        self.query["certificates"] = ",".join(
            [isinstance(v, str) and v or v.value for v in certificates]
        )
        self.query["colors"] = ",".join(
            [isinstance(v, str) and v or v.value for v in colors]
        )
        self.query["countries"] = ",".join(
            [isinstance(v, str) and v or v.value for v in countries]
        )
        self.query["keywords"] = keywords
        self.query["languages"] = ",".join(
            [isinstance(v, str) and v or v.value for v in languages]
        )
        self.query["locations"] = locations
        self.query["moviemeter-min"] = moviemeter[0]
        self.query["moviemeter-max"] = moviemeter[1]
        self.query["plot"] = plot
        self.query["runtime-min"] = runtime[0]
        self.query["runtime-max"] = runtime[1]
        self.query["sound_mixes"] = ",".join(
            [isinstance(v, str) and v or v.value for v in sound_mixes]
        )
        self.query["my_ratings"] = ",".join(
            [isinstance(v, str) and v or v.value for v in my_ratings]
        )
        self.query["now_playing"] = ",".join(
            [isinstance(v, str) and v or v.value for v in now_playing]
        )
        self.query["adult"] = ",".join(
            [isinstance(v, str) and v or v.value for v in adult]
        )
