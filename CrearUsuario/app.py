import logging
import pymysql
import json
import random
import string
import boto3
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "prodLien"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except KeyError as e:
        logging.exception('Error al acceder a la dict')
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}


def lambda_handler(event, context):
    connection = None
    try:
        secret = get_secret()
        host = secret.get("host")
        user = secret.get("username")
        passw = secret.get("password")
        db = secret.get("dbInstanceIdentifier")

        if not all([host, user, passw, db]):
            raise ValueError("Faltan uno o más parámetros requeridos en el secreto.")

        user_groups = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('cognito:groups', [])

        if 'admin' not in user_groups:
            return {
                'statusCode': 403,
                'headers': HEADERS,
                'body': json.dumps('Acceso denegado. Solo los administradores pueden realizar esta acción.')
            }

        request_body = json.loads(event['body'])
        nombre = request_body.get('nombre')
        email = request_body.get('email')
        fechanacimiento = request_body.get('fechanacimiento')
        phone = request_body.get('phone')
        user_name = request_body.get('username')
        password = generate_temporary_password()

        if not all([email, user_name, nombre, fechanacimiento, phone]):
            return {
                "statusCode": 400,
                'headers': HEADERS,
                "body": json.dumps({"message": "Faltan parámetros de entrada"})
            }

        client = boto3.client('cognito-idp', region_name='us-east-2')
        user_pool_id = "us-east-2_Dak0N3NUX"

        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=user_name,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'false'},
            ],
            TemporaryPassword=password
        )

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