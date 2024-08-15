import json

from EliminarUsuario import app
import unittest


class TestApp(unittest.TestCase):

    def test_lamnda_DeleteBook(self):
        mock = {
            'body': json.dumps({
                'username':'papichulo32'
            })
        }
        __ = None

        regreso = app.lambda_handler(mock, __)
        print(regreso)
