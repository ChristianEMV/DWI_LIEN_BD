import json
import unittest

from BajaPrestamo import app

class TestApp(unittest.TestCase):
    def test_lambda_post(self):
        mock = {
            'body': json.dumps({
                'idprestamo': '14',
                'idbook': '49'
            })
        }
        __ = None

        regreso = app.lambda_handler(mock,__)
        print(regreso)

