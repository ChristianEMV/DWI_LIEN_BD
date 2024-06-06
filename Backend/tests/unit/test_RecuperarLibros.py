

from Backend.book.RecupearLibros.RecupearLibros import lambda_handler


def test_lamnda_AllBooks():

    regreso = lambda_handler()
    print(regreso)