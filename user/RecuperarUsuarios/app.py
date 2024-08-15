import logging
import pymysql
import json
from datetime import date
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
    except ClientError as e:
        logging.exception('Error al acceder al secreto')
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}

def lambda_handler(event, context):
    user_groups = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('cognito:groups', [])

    if 'admin' not in user_groups:
        return {
            'statusCode': 403,
            'headers': HEADERS,
            'body': json.dumps('Acceso denegado. Solo los administradores pueden realizar esta acción.')
        }

    secret = get_secret()
    host = secret.get("host")
    user = secret.get("username")
    passw = secret.get("password")
    db = secret.get("dbInstanceIdentifier")

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM users"
            cursor.execute(select_query)
            results = cursor.fetchall()

            users = []
            for result in results:
                USERNEW = {
                    'iduser': result[0],
                    'nombre': result[1],
                    'email': result[2],
                    'fechanacimiento': result[3].isoformat() if isinstance(result[3], date) else result[3],
                    'phone': result[4],
                    'username': result[5],
                }
                users.append(USERNEW)

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(users)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al recuperar los usuarios: {str(e)}')
        }

    finally:
        connection.close()