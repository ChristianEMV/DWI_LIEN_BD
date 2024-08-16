import logging
import boto3
from botocore.exceptions import ClientError
import pymysql
import json
from datetime import date

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
        logging.error('Error al obtener el secreto: %s', e)
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}

def lambda_handler(event, context):
    try:
        secret = get_secret()
        host = secret.get("host")
        user = secret.get("username")
        password = secret.get("password")
        db = secret.get("dbInstanceIdentifier")

        if not all([host, user, password, db]):
            raise ValueError("Faltan uno o más parámetros requeridos en el secreto")

        connection = pymysql.connect(host=host, user=user, password=password, db=db)

        try:
            with connection.cursor() as cursor:
                select_query = "SELECT * FROM books"
                cursor.execute(select_query)
                results = cursor.fetchall()

                books = []
                for result in results:
                    book = {
                        'idbook': result[0],
                        'titulo': result[1],
                        'fecha_publicacion': result[2].isoformat() if isinstance(result[2], date) else result[2],
                        'autor': result[3],
                        'editorial': result[4],
                        'status': result[5],
                        'descripcion': result[6],
                        'categoria': result[7],
                    }
                    books.append(book)

        except pymysql.MySQLError as e:
            return {
                'statusCode': 500,
                'headers': HEADERS,
                'body': json.dumps(f'Error al ejecutar la consulta: {str(e)}')
            }
        finally:
            connection.close()

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(books)
        }

    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps(f'Error de parámetros: {str(e)}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error: {str(e)}')
        }
