import pymysql
import json
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
        user_name = request_body.get('user_name')

        if not user_name:
            return {
                "statusCode": 400,
                'headers': HEADERS,
                "body": json.dumps({"message": "Falta el parámetro 'user_name'"})
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
