import json

from Backend.book.EliminarLibro.EliminarLibro import lambda_handler


def test_lamnda_DeleteBook():
    mock = {
        'body': json.dumps({
            'idbook': '20',
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)