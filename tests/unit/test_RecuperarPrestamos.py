import unittest
import json
from unittest.mock import patch

from RecuperarPrestamos import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }

    @patch('RecuperarPrestamos.app.pymysql.connect')
    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_admin_access(self, mock_get_secret, mock_connect):
        # Simula la respuesta de get_secret
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbname': 'test_db'
        }

        # Simula la conexión y la consulta SQL
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [
            (1, '2024-01-01', '2024-01-15', 100, 200, 'Test Book', '2020-01-01', 'Author', 'Editorial', 'available', 'Description', 'Category')
        ]

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertDictEqual(response['headers'], self.headers)
        self.assertIn('Test Book', response['body'])

    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_secret_error(self, mock_get_secret):
        # Simula un error en la obtención de secretos
        mock_get_secret.side_effect = Exception('Error al obtener secreto')

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error al obtener secreto', response['body'])

    @patch('RecuperarPrestamos.app.pymysql.connect')
    def test_lambda_handler_db_connection_error(self, mock_connect):
        # Simula un error en la conexión a la base de datos
        mock_connect.side_effect = Exception('Error al conectar a la base de datos')

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error al conectar a la base de datos', response['body'])

    @patch('RecuperarPrestamos.app.pymysql.connect')
    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_no_results(self, mock_get_secret, mock_connect):
        # Simula la respuesta de get_secret
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbname': 'test_db'
        }

        # Simula la conexión y la consulta SQL sin resultados
        mock_connection = mock_connect.return_value
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = []

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['admin']
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertDictEqual(response['headers'], self.headers)
        self.assertEqual(json.loads(response['body']), [])


    @patch('RecuperarPrestamos.app.pymysql.connect')
    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_non_admin_access(self, mock_get_secret, mock_connect):
        # Simula la respuesta de get_secret
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbname': 'test_db'
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']  # Usuario no administrador
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 403)
        # Decodifica el JSON del cuerpo de la respuesta
        response_body = json.loads(response['body'])
        # Verifica que el mensaje de error esperado esté en el cuerpo de la respuesta decodificado
        self.assertEqual(response_body, 'Acceso denegado. Solo los administradores pueden realizar esta acción.')



if __name__ == '__main__':
    unittest.main()