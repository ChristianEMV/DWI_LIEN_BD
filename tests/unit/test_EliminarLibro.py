import json

from book.EliminarLibro import app

import unittest


class TestApp(unittest.TestCase):

    def test_lambda_post(self):
        mock = {
            'pathParameters': {
                'idbook': '54'
            }
        }
        __ = None
        regreso = app.lambda_handler(mock, __)
        print(regreso)
