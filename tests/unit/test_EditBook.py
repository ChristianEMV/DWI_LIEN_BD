import json

from Backend.book.EditBook.app import lambda_handler


def test_lambda_post():
    mock = {
        'body': json.dumps({
            'idbook':'1',
            'titulo': 'EL gordito tiste',
            'fecha_publicacion': '2024-06-07',
            'autor': 'SAMUEL',
            'editorial': 'La casa de los sueños',
            'status': '0'
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)