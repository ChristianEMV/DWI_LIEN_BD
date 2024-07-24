from book.RecuperarLibrosByTitulo import app

import unittest

import json


class TestApp(unittest.TestCase):

    def test_lamnda_AllBooksOrderDate(self):
        event = {
            'queryStringParameters': {
                'title': 'El '
            }
        }
        __ = None

        regreso = app.lambda_handler(event, __)
        print(regreso)