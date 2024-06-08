import json

from Backend.book.RecuperarLibro.app import lambda_handler


def test_lamnda_FindById():
    mock = {
        'body': json.dumps({
            'idbook': '1',
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)