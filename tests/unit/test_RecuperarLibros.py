import unittest
from unittest.mock import patch, Mock
import json
from book.RecupearLibros import app
from datetime import date

class TestApp(unittest.TestCase):

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_missing_secret_field(self, mock_get_secret, mock_connect):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
        }

        event = {}
        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Faltan uno o más parámetros requeridos en el secreto', json.loads(response['body']))

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_sql_query_error(self, mock_get_secret, mock_connect):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        def mock_cursor():
            class Cursor:
                def execute(self, *args, **kwargs):
                    raise app.pymysql.MySQLError("Error al ejecutar la consulta")

                def fetchall(self):
                    return []

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    pass

            return Cursor()

        mock_connect.return_value.cursor = mock_cursor
        event = {}
        response = app.lambda_handler(event, None)

        expected_body = 'Error al ejecutar la consulta: Error al ejecutar la consulta'
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_database_connection_close_error(self, mock_get_secret, mock_connect):
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

                def fetchall(self):
                    return [
                        (1, 'Test Book', '2024-01-01', 'Test Author', 'Test Publisher', 'available', 'Test Description',
                         'Fiction')
                    ]

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    pass

            return Cursor()

        class MockConnection:
            def cursor(self):
                return mock_cursor()

            def close(self):
                # Simular un error al cerrar la conexión
                raise Exception("Error al cerrar la conexión")

        mock_connect.return_value = MockConnection()

        event = {}  # Simular un evento vacío o con datos irrelevantes
        response = app.lambda_handler(event, None)

        expected_body = 'Error: Error al cerrar la conexión'
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expected_body)

    @patch('book.RecupearLibros.app.get_secret')
    def test_get_secret_error(self, mock_get_secret):
        mock_get_secret.side_effect = Exception('Error al obtener el secreto')

        event = {}
        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Error al obtener el secreto', json.loads(response['body']))

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_cursor_fetchall_error(self, mock_get_secret, mock_connect):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        class MockCursor:
            def execute(self, *args, **kwargs):
                pass

            def fetchall(self):
                raise Exception('Error al recuperar datos del cursor')

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

        class MockConnection:
            def cursor(self):
                return MockCursor()

            def close(self):
                pass

        mock_connect.return_value = MockConnection()

        event = {}
        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Error al recuperar datos del cursor',
                      json.loads(response['body']))

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_network_error(self, mock_get_secret, mock_connect):
        mock_get_secret.return_value = {
            'host': 'test_host',
            'username': 'test_user',
            'password': 'test_password',
            'dbInstanceIdentifier': 'test_db'
        }

        mock_connect.side_effect = Exception('Network error')

        event = {}
        response = app.lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error: Network error', json.loads(response['body']))

    @patch('book.RecupearLibros.app.pymysql.connect')
    @patch('book.RecupearLibros.app.get_secret')
    def test_empty_data(self, mock_get_secret, mock_connect):
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

                def fetchall(self):
                    return []

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_value, traceback):
                    pass

            return Cursor()

        mock_connect.return_value.cursor = mock_cursor
        event = {}
        response = app.lambda_handler(event, None)

        expected_body = []
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected_body)
