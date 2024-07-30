import json

import unittest


from book.RecuperarLibro.app import lambda_handler


class TestApp(unittest.TestCase):

    def test_lamnda_FindById(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': '["admin"]'  # El token debe indicar que el usuario pertenece al grupo 'admin'
                    }
                }
            },
            'pathParameters': {
                'idbook': '1'
            }
        }
        __ = None

        regreso = lambda_handler(event, __)
        print(regreso)