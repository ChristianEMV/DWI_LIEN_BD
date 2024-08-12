import json
import unittest

from BajaPrestamo import app

class TestApp(unittest.TestCase):
    def test_lambda_post(self):
        mock = {
            'body': json.dumps({
                'idprestamo': '9',
                'idbook': '46'
            })
        }
        __ = None

        regreso = app.lambda_handler(mock,__)
        print(regreso)

