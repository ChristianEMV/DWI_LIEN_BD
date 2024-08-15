import logging
import pymysql
import json
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
        user_name = request_body.get('username')

        if not user_name:
            return {
                "statusCode": 400,
                'headers': HEADERS,
                "body": json.dumps({"message": "Falta el parámetro 'username'"})
            }

        client = boto3.client('cognito-idp', region_name='us-east-2')
        user_pool_id = "us-east-2_Dak0N3NUX"

        client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=user_name
        )

        connection = pymysql.connect(host=host, user=user, password=passw, db=db)
        with connection.cursor() as cursor:
            sql = "DELETE FROM users WHERE username = %s"
            cursor.execute(sql, (user_name,))
            connection.commit()

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(f'Usuario {user_name} eliminado exitosamente')
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps(f'Error al eliminar usuario de Cognito: {e.response["Error"]["Message"]}')
        }
    except Exception as e:
        if connection:
            connection.rollback()
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al eliminar usuario: {str(e)}')
        }
    finally:
        if connection:
            connection.close()