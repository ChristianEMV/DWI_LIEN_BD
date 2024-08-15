from user.RecuperarUsuarios import app

import unittest

import json


class TestApp(unittest.TestCase):

    def test_lamnda_AllUsers(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },

        }
        __ = None

        regreso = app.lambda_handler(event, __)
        print(regreso)