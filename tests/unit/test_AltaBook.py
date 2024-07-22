import json

from book.AltaBook import app
import unittest


class TestApp(unittest.TestCase):
    def test_lambda_post(self):
        mock = {
            'body': json.dumps({
                'titulo': 'EL gordito tiste',
                'fecha_publicacion': '2024-06-07',
                'autor': 'Juan Araujo 2',
                'editorial': 'La casa de los sueños',
                'status': '1'
            })
        }
        __ = None
        regreso = app.lambda_handler(mock,__)
        print(regreso)
