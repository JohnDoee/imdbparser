import argparse
import logging
from pprint import pprint


def main():
    from .imdb import IMDb, CHART_TYPES, AS

    parser = argparse.ArgumentParser(description="Fetch info from IMDb")
    parser.add_argument("--debug", help="Enable debugging", action="store_true")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    fetch_parser = subparsers.add_parser(name="fetch")
    fetch_parser.add_argument("imdb_id", help="an IMDb id, e.g. tt0120737")

    search_parser = subparsers.add_parser(
        name="search", description="Search for a movie or tv show"
    )
    search_parser.add_argument(
        "type", help="Type to search for", choices=["tv", "movie"]
    )
    search_parser.add_argument("title", help="Title to search for")

    resolve_parser = subparsers.add_parser(
        name="resolve", description="Try to resolve a search into a specific entry"
    )
    resolve_parser.add_argument(
        "type", help="Type to search-resolve for", choices=["tv", "movie"]
    )
    resolve_parser.add_argument("title", help="Title to search-resolve for")
    resolve_parser.add_argument(
        "year", help="Year close to the entry", type=int, nargs="?"
    )

    chart_parser = subparsers.add_parser(name="chart", description="Fetch a chart")
    chart_parser.add_argument("type", help="Chart type", choices=CHART_TYPES)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    i = IMDb()
    movie = None
    movies = None

    if args.command == "fetch":
        movie = i.get_movie(args.imdb_id.lstrip("tt"))
    elif args.command == "search":
        if args.type == "tv":
            movies = i.search_tv_show(args.title)
        elif args.type == "movie":
            movies = i.search_movie(args.title)
    elif args.command == "resolve":
        if args.type == "tv":
            movie = i.resolve_tv_show(args.title, args.year)
        elif args.type == "movie":
            movie = i.resolve_movie(args.title, args.year)
    elif args.command == "chart":
        movies = i.get_chart(args.type)
    else:
        parser.print_help()

    if movie is not None:
        movie.fetch()
        pprint(movie.__dict__)
        print("")
        print("More like this")
        for recommended_movie in movie.more_like_this:
            pprint(recommended_movie.__dict__)

    if movies is not None:
        movies.fetch()
        if movies.results:
            for movie in movies.results:
                print(movie)
                print(movie.__dict__)
        else:
            print("Nothing found...")


if __name__ == "__main__":
    main()
