import unittest
import json
import pymysql
from datetime import date
import boto3
from botocore.exceptions import ClientError
from unittest.mock import patch, MagicMock

# Suponiendo que tu función Lambda está en el archivo RecuperarPrestamos.py
from RecuperarPrestamos import app

class TestApp(unittest.TestCase):

    def setUp(self):
        # Configuración inicial, si es necesario
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'GET, OPTIONS'
        }

    @patch('RecuperarPrestamos.app.boto3.session.Session.client')
    def test_lambda_handler_admin_access(self, mock_boto_client):
        # Simular la respuesta del cliente de boto3
        mock_client = mock_boto_client.return_value
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test_host',
                'username': 'test_user',
                'password': 'test_password',
                'dbname': 'test_db'
            })
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
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers'], self.headers)
        # Puedes agregar más aserciones para verificar el contenido de 'body'

    @patch('RecuperarPrestamos.app.boto3.session.Session.client')
    def test_lambda_handler_non_admin_access(self, mock_boto_client):
        # Simular la respuesta del cliente de boto3
        mock_client = mock_boto_client.return_value
        mock_client.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test_host',
                'username': 'test_user',
                'password': 'test_password',
                'dbname': 'test_db'
            })
        }

        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'cognito:groups': ['user']
                    }
                }
            }
        }
        context = None
        response = app.lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(response['headers'], self.headers)
        self.assertEqual(json.loads(response['body']),
                         'Acceso denegado. Solo los administradores pueden realizar esta acción.')

    @patch('RecuperarPrestamos.app.pymysql.connect')
    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_database_query(self, mock_get_secret, mock_pymysql_connect):
        # Configurar los mocks para simular una respuesta exitosa
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbname': 'test_db'
        }

        mock_connection = mock_pymysql_connect.return_value
        mock_cursor = mock_connection.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, 'Titulo 1', '2024-08-11', 'Descripcion 1', 'Estatus 1', 'url1'),
            (2, 'Titulo 2', '2024-08-12', 'Descripcion 2', 'Estatus 2', 'url2')
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
        self.assertEqual(response['headers'], self.headers)
        body = json.loads(response['body'])
        self.assertIsInstance(body, list)
        self.assertEqual(len(body), 2)

    @patch('RecuperarPrestamos.app.pymysql.connect')
    @patch('RecuperarPrestamos.app.get_secret')
    def test_lambda_handler_database_error(self, mock_get_secret, mock_pymysql_connect):
        # Configurar los mocks para simular un error en la base de datos
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbname': 'test_db'
        }

        mock_pymysql_connect.side_effect = pymysql.MySQLError('Database connection failed')

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
        self.assertEqual(response['headers'], self.headers)

    @patch('RecuperarPrestamos.app.boto3.session.Session.client')
    def test_lambda_handler_missing_secret(self, mock_boto_client):
        # Configurar el mock para simular un error al recuperar el secreto
        mock_boto_client.return_value.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}},
            "GetSecretValue"
        )

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
        self.assertEqual(response['headers'], self.headers)

if __name__ == '__main__':
    unittest.main()
