from automaton.ombi.movie import MovieRequestMixin
from tests.ombi.fixtures import movie_search_response


def test_get_response_from_ombi_movie_data():
    choices = MovieRequestMixin._get_response_from_ombi_movie_data(movie_search_response)
    assert choices == {
        0: {
            "title": "The Matrix",
            "id": "603",
            'release': '(1999)'
        },
        1: {
            "title": "The Matrix Reloaded",
            "id": "604",
            'release': '(2003)'
        },
        2: {
            "title": "The Matrix Revolutions",
            "id": "605",
            'release': '(2003)'
        },
        3: {
            "title": "The Matrix Revisited",
            "id": "14543",
            'release': '(2001)'
        },
        4: {
            "title": "The Matrix Recalibrated",
            "id": "221495",
            'release': '(2004)'
        },
        5: {
            "title": "Sex and the Matrix",
            "id": "344225",
            'release': '(2000)'
        }
    }
