import json

import bcrypt

from Backend.User.CrearUsuario.ConnectionDB import get_connection


def lambda_handler(event):
    try:
        request_body = json.loads(event['body'])
        nombre = request_body.get('nombre')
        email = request_body.get('email')
        fechanacimiento = request_body.get('fechanacimiento')
        rol = request_body.get('rol')
        password = request_body.get('password')

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        connection = get_connection()

        with connection.cursor() as cursor:
            sql = "INSERT INTO users (nombre, email, fechanacimiento, rol, password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, fechanacimiento, rol, hashed_password.decode()))
        connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps('Usuario creado exitosamente')
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error al crear usuario: {str(e)}')
        }
    finally:
        connection.close()
