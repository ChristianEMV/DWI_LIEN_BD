import json

import unittest


from book.RecuperarLibro.app import lambda_handler


class TestApp(unittest.TestCase):

    def test_lamnda_FindById(self):
        mock = {
            'body': json.dumps({
                'idbook': '1',
            })
        }
        __ = None

        regreso = lambda_handler(mock, __)
        print(regreso)