from book.RecupearLibros import app

import unittest

import json


class TestApp(unittest.TestCase):

    def test_lamnda_AllBooks(self):
        event = {}
        __ = None

        regreso = app.lambda_handler(event, __)
        print(regreso)