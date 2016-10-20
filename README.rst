imdbparser
==========

Search IMDb and get movie information.
Incredibly basic, limited feature-set, somewhat fast.

Usage
-----

Get from ID
~~~~~~~~~~~
.. code-block:: python

    >>> from imdbparser import IMDb
    >>> imdb = IMDb()
    >>> movie = imdb.get_movie(1954470)
    >>> movie.fetched
    False
    >>> movie.fetch()
    >>> movie.fetched
    True
    >>> movie.__dict__
    ...


Search
~~~~~~
.. code-block:: python

    >>> from imdbparser import IMDb
    >>> imdb = IMDb()
    >>> search_result = imdb.search_movie('Matrix')
    >>> search_result.fetched
    False
    >>> search_result.fetch()
    >>> search_result.fetched
    True
    >>> search_result.results
    [<Movie fetched=False imdb_id='0133093' title='The Matrix' year=1999>,
     <Movie fetched=False imdb_id='0234215' title='The Matrix Reloaded' year=2003>, ...]

.. code-block:: python

    >>> from imdbparser import IMDb
    >>> imdb = IMDb()
    >>> search_result = imdb.search_tv_show('it crowd')
    >>> search_result.fetched
    False
    >>> search_result.fetch()
    >>> search_result.fetched
    True
    >>> search_result.results
    [<Movie fetched=False imdb_id='0487831' title='The IT Crowd' year=None>,
     <Movie fetched=False imdb_id='0944954' title='The IT Crowd' year=None>, ...]





License
-------

MIT, see LICENSE