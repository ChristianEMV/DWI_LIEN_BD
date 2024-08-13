import pymysql
import json
import random
import string
import boto3
from botocore.exceptions import ClientError

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
    connection = None
    try:
        request_body = json.loads(event['body'])
        nombre = request_body.get('nombre')
        email = request_body.get('email')
        fechanacimiento = request_body.get('fechanacimiento')
        phone = request_body.get('phone')

        user_name = request_body.get('user_name')
        password = generate_temporary_password()

        if not all([email, user_name, nombre, fechanacimiento, phone]):
            return {
                "statusCode": 400,
                'headers': HEADERS,
                "body": json.dumps({"message": "Faltan parámetros de entrada"})
            }

        client = boto3.client('cognito-idp', region_name='us-east-2')
        user_pool_id = "us-east-2_Dak0N3NUX"

        # Crea el usuario en Cognito con una contraseña temporal
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=user_name,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'},
            ],
            TemporaryPassword=password
        )

        # Asigna el usuario al grupo "usuario"
        client.admin_add_user_to_group(
            UserPoolId=user_pool_id,
            Username=user_name,
            GroupName="usuario"
        )

        connection = pymysql.connect(host=host, user=user, password=passw, db=db)

        with connection.cursor() as cursor:
            sql = "INSERT INTO users (nombre, email, fechanacimiento, username, phone) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, fechanacimiento, user_name, phone))

            connection.commit()
            return {
                'statusCode': 200,
                'headers': HEADERS,
                'body': json.dumps('Usuario creado exitosamente')
            }
    except Exception as e:
        if connection:
            connection.rollback()
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al crear usuario: {str(e)}')
        }
    finally:
        if connection:
            connection.close()


def generate_temporary_password(length=12):
    special_characters = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`+= '
    characters = string.ascii_letters + string.digits + special_characters

    while True:
        password = ''.join(random.choice(characters) for _ in range(length))

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in special_characters for char in password)

        if has_digit and has_upper and has_lower and has_special and len(password) >= 8:
            return password