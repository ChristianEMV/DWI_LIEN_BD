import json

from CrearUsuario import app
import unittest


class TestApp(unittest.TestCase):

    def test_lamnda_DeleteBook(self):
        mock = {
            'body': json.dumps({
                'username':'papichulo32',
                'nombre': 'Daniela',
                'email': 'xelece3b507@biscoine.com',
                'fechanacimiento': '1998/12/12',
                'phone':'7773187812',

            })
        }
        __ = None

        regreso = app.lambda_handler(mock, __)
        print(regreso)
