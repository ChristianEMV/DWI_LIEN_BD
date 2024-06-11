import json

from Backend.book.EliminarLibro.app import lambda_handler


def test_lamnda_DeleteBook():
    mock = {
        'body': json.dumps({
            'idbook': '2',
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)