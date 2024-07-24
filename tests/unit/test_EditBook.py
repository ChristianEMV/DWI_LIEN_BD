import json


from book.EditBook import app

import unittest


class TestApp(unittest.TestCase):
    def test_lambda_post(self):
        mock = {
            'body': json.dumps({
                'idbook': '21',
                'titulo': 'EL gordito tiste',
                'fecha_publicacion': '2024-06-07',
                'autor': 'SAMUEL',
                'editorial': 'La casa de los sueños',
                'status': '0',
                'descripcion': 'hola',
                'categoria': 'hola'
            })
        }
        __ = None
        regreso = app.lambda_handler(mock, __)
        print(regreso)