import json

from Backend.CrearUsuario import app


def test_lamnda_DeleteBook():
    mock = {
        'body': json.dumps({
            'nombre': 'Daniela',
            'email': 'teste@gmail.com',
            'fechanacimiento': '16/11/1998',
            'rol': '2',
            'password': 'mariana',

        })
    }

    regreso = app.lambda_handler(mock)
    print(regreso)