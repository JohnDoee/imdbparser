import argparse

from pprint import pprint

def main():
    parser = argparse.ArgumentParser(description='Fetch info from IMDb')
    parser.add_argument('imdb_id', help='an IMDb id, e.g. tt0120737')

    args = parser.parse_args()

    from .imdb import IMDb
    i = IMDb()
    movie = i.get_movie(args.imdb_id.lstrip('tt'))
    movie.fetch()
    pprint(movie.__dict__)


if __name__ == '__main__':
    main()
