from RecuperarPrestamos import app

import unittest

import json


class TestApp(unittest.TestCase):

    def test_lamnda_AllBooks(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'pathParameters': {
                'idbook': '44'
            }
        }
        __ = None

        regreso = app.lambda_handler(event, __)
        print(regreso)