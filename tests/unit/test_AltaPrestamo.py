import json

from Backend.Altaprestamo import app

def test_lambda_post():
    mock = {
        'body': json.dumps({
            'fecha_inicio': '2024-06-07',
            'fecha_fin': '2024-06-19',
            'iduser': '2',
            'idbook': '1'
        })
    }

    regreso = app.lambda_handler(mock)
    print(regreso)

