from unittest.mock import patch
import json
import unittest
from book.AltaBook import app


class TestApp(unittest.TestCase):

    @patch('book.AltaBook.app.pymysql.connect')
    @patch('book.AltaBook.app.get_secret')
    def test_lambda_handler_success(self, mock_get_secret, mock_connect):
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

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Libro registrado exitosamente')

    def test_missing_request_body_field(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'body': json.dumps({
                'titulo': 'Test Book',
                # 'fecha_publicacion': campo faltante
                'autor': 'Test Author',
                'editorial': 'Test Publisher',
                'status': 'available',
                'descripcion': 'Test Description',
                'categoria': 'Fiction'
            })
        }

        response = app.lambda_handler(event, None)
        response_body = json.loads(response['body'])  # Parse the response body

        self.assertEqual(response['statusCode'], 400)
        self.assertIn(
            'Error en los datos de entrada: El campo "fecha_publicacion" es requerido y no puede estar vacío',
            response_body
        )

    def test_user_not_authorized(self):
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']
                    }
                }
            },
            'body': json.dumps({
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
        response_body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 403)
        self.assertIn('Acceso denegado. Solo los administradores pueden realizar esta acción.', response_body)

    @patch('book.AltaBook.app.get_secret')
    def test_missing_parameters_in_secret(self, mock_get_secret):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
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
        response_body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Faltan uno o más parámetros requeridos en el secreto', response_body)

    @patch('book.AltaBook.app.get_secret')
    def test_error_accessing_secrets(self, mock_get_secret):
        mock_get_secret.side_effect = Exception("Error al obtener el secreto")

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            },
            'body': json.dumps({
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
        response_body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error al obtener las credenciales', response_body)
