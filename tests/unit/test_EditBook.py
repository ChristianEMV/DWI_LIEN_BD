import json

from unittest.mock import patch
import unittest
from book.EditBook import app



class TestApp(unittest.TestCase):

    @patch('book.EditBook.app.get_secret')
    def test_missing_secret_field(self, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password'
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'body': json.dumps({
                'idbook': '54',
                'titulo': 'Test Book',
                'fecha_publicacion': '2024-01-01',
                'autor': 'Test Author',
                'editorial': 'Test Publisher',
                'status': 'available',
                'descripcion': 'Test Description',
                'categoria': 'Fiction'
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error en los datos de entrada: Faltan uno o m\\u00e1s par\\u00e1metros requeridos en el secreto.', response['body'])

    @patch('book.EditBook.app.pymysql.connect')
    @patch('book.EditBook.app.get_secret')
    def test_database_connection_error(self, mock_get_secret, mock_connect):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        mock_connect.side_effect = Exception('Error de conexión a la base de datos')

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'body': json.dumps({
                'idbook': '54',
                'titulo': 'Test Book',
                'fecha_publicacion': '2024-01-01',
                'autor': 'Test Author',
                'editorial': 'Test Publisher',
                'status': 'available',
                'descripcion': 'Test Description',
                'categoria': 'Fiction'
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error en la petici\\u00f3n: Error de conexi\\u00f3n a la base de datos', response['body'])

    def test_malformed_json_body(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'body': '{idbook: 54, titulo: Test Book}'  # JSON malformado
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Error en los datos de entrada: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)', response['body'])

    def test_unauthorized_user_group(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']
                    }
                }
            },
            'body': json.dumps({
                'idbook': '54',
                'titulo': 'Test Book',
                'fecha_publicacion': '2024-01-01',
                'autor': 'Test Author',
                'editorial': 'Test Publisher',
                'status': 'available',
                'descripcion': 'Test Description',
                'categoria': 'Fiction'
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 403)
        self.assertIn('Acceso denegado', response['body'])

    @patch('book.EditBook.app.pymysql.connect')
    @patch('book.EditBook.app.get_secret')
    def test_update_nonexistent_book(self, mock_get_secret, mock_connect):
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

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    pass

                @property
                def rowcount(self):
                    return 0

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
            'body': json.dumps({
                'idbook': '999',
                'titulo': 'Nonexistent Book',
                'fecha_publicacion': '2024-01-01',
                'autor': 'Unknown Author',
                'editorial': 'Unknown Publisher',
                'status': 'unavailable',
                'descripcion': 'No description',
                'categoria': 'Unknown'
            })
        }

        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Libro no encontrado', response['body'])