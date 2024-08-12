import json

from CambiarContrasenia import app
import unittest


class TestApp(unittest.TestCase):

    def test_lamnda_DeleteBook(self):
        mock = {
            'body': json.dumps({
                'username':'papichulo',
                'temporary_password': 'W=F7\VaCa=Bb',
                'new_password': 'Testc123@',
            })
        }
        __ = None

        regreso = app.lambda_handler(mock, __)
        print(regreso)