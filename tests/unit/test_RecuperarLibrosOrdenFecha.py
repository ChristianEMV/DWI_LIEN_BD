from book.RecuperarLibrosOrdenFecha import app

import unittest

import json


class TestApp(unittest.TestCase):

    def test_lamnda_AllBooksOrderDate(self):
        event = {
            'queryStringParameters': {
                'order': 'asc'
            }
        }
        __ = None

        regreso = app.lambda_handler(event, __)
        print(regreso)