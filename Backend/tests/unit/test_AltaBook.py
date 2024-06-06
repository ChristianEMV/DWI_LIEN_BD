import json

from Backend.book.AltaBook.AltaBook import lambda_handler


def test_lambda_post():
    mock = {
        'body': json.dumps({
            'titulo': 'EL gordito tiste',
            'fecha_publicacion': '2024-06-07',
            'autor': 'Juan Araujo',
            'editorial': 'La casa de los sueños',
            'status': '1'
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)
