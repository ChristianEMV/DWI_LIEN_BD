import json
from book.EliminarLibro import app
from unittest import mock
import unittest


class TestApp(unittest.TestCase):

    def test_access_denied_non_admin(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']
                    }
                }
            },
            'pathParameters': {
                'idbook': '54'
            }
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertIn('Acceso denegado', response['body'])

    def test_missing_idbook(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'pathParameters': {
                'idbook': ''
            }
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('El campo \\"idbook\\" es requerido y no puede estar vac\\u00edo.', response['body'])

    def test_book_not_found(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'pathParameters': {
                'idbook': '9999'
            }
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Libro no encontrado', response['body'])

    def test_successful_deletion(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'pathParameters': {
                'idbook': '35'
            }
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Libro eliminado exitosamente', response['body'])

    def test_database_error(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'pathParameters': {
                'idbook': '54'
            }
        }

        with unittest.mock.patch('pymysql.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection error")

            response = app.lambda_handler(event, None)

            self.assertEqual(response['statusCode'], 500)
            self.assertIn('Error en la petici\\u00f3n: Database connection error', response['body'])