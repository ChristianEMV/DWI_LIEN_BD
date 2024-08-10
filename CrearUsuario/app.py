import bcrypt
import json
import pymysql


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}


def lambda_handler(event, __):
    try:
        request_body = json.loads(event['body'])
        nombre = request_body.get('nombre')
        email = request_body.get('email')
        fechanacimiento = request_body.get('fechanacimiento')
        rol = request_body.get('rol')
        password = request_body.get('password')


        connection = pymysql.connect(host=host, user=user, password=passw, db=db)

        with connection.cursor() as cursor:
            sql = "INSERT INTO users (nombre, email, fechanacimiento, rol, password) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, fechanacimiento, rol, password))
        connection.commit()

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps('Usuario creado exitosamente bebe')
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al crear usuario: {str(e)}')
        }
    finally:
        connection.close()
