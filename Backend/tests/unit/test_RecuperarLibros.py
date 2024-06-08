

from Backend.book.RecupearLibros.app import lambda_handler


def test_lamnda_AllBooks():

    regreso = lambda_handler()
    print(regreso)