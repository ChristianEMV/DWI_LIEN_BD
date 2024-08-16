from unittest.mock import patch, Mock
import unittest
import json
from book.RecuperarLibro import app

class TestApp(unittest.TestCase):

    @patch('book.RecuperarLibro.app.get_secret')
    @patch('book.RecuperarLibro.app.pymysql.connect')
    def test_lambda_access_denied(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']
                    }
                }
            },
            'pathParameters': {
                'idbook': '44'
            }
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body']),
                         'Acceso denegado. Solo los administradores pueden realizar esta acción.')

    @patch('book.RecuperarLibro.app.get_secret')
    @patch('book.RecuperarLibro.app.pymysql.connect')
    def test_lambda_missing_idbook(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            }
        }
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), 'Parámetro idbook es requerido')

    @patch('book.RecuperarLibro.app.get_secret')
    @patch('book.RecuperarLibro.app.pymysql.connect')
    def test_lambda_connection_error(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        mock_connect.side_effect = Exception('Connection error')

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
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error desconocido: Connection error', json.loads(response['body']))

    @patch('book.RecuperarLibro.app.get_secret')
    @patch('book.RecuperarLibro.app.pymysql.connect')
    def test_lambda_query_error(self, mock_connect, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        def mock_cursor():
            class Cursor:
                def execute(self, *args, **kwargs):
                    pass

                def fetchone(self):
                    raise app.pymysql.MySQLError('Query error')

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    pass

            return Cursor()

        mock_connect.return_value.cursor = mock_cursor

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
        response = app.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error al recuperar el libro: Query error', json.loads(response['body']))

