import json

from Backend.prestamos.Altaprestamo.AltaPrestamo import lambda_handler

def test_lambda_post():
    mock = {
        'body': json.dumps({
            'fecha_inicio': '2024-06-07',
            'fecha_fin': '2024-06-19',
            'iduser': '2',
            'idbook': '1'
        })
    }

    regreso = lambda_handler(mock)
    print(regreso)

