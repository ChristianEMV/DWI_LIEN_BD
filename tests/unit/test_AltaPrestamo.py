import json
import unittest

from Altaprestamo import app

class TestApp(unittest.TestCase):
    def test_lambda_post(self):
        mock = {
            'body': json.dumps({
                'fecha_inicio': '2024-06-07',
                'fecha_fin': '2024-06-19',
                'iduser': '2',
                'idbook': '1'
            })
        }
        __ = None

        regreso = app.lambda_handler(mock,__)
        print(regreso)

