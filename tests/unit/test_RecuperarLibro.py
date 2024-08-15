import json

import unittest


from book.RecuperarLibro.app import lambda_handler


import unittest
import json

class TestApp(unittest.TestCase):

    def test_lambda_FindById(self):
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

        response = lambda_handler(event, __)
        print(response)
        self.assertEqual(response['statusCode'], 200)

if __name__ == '__main__':
    unittest.main()