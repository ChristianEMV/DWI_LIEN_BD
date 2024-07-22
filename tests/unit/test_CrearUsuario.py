import json

from CrearUsuario import app
import unittest


class TestApp(unittest.TestCase):

    def test_lamnda_DeleteBook(self):
        mock = {
            'body': json.dumps({
                'nombre': 'Daniela',
                'email': 'teste@gmail.com',
                'fechanacimiento': '16/11/1998',
                'rol': '2',
                'password': 'mariana',

            })
        }
        __ = None

        regreso = app.lambda_handler(mock, __)
        print(regreso)
