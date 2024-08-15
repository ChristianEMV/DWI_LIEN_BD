import logging
import boto3
from botocore.exceptions import ClientError
import pymysql
import json

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
    'Access-Control-Allow-Methods': 'DELETE, OPTIONS'
}

def lambda_handler(event, __):
    try:
        secret = get_secret()
        host = secret.get("host")
        user = secret.get("username")
        password = secret.get("password")
        db = secret.get("dbInstanceIdentifier")

        if not all([host, user, password, db]):
            raise ValueError("Faltan uno o más parámetros requeridos en el secreto.")

        idbook = event.get('pathParameters', {}).get('idbook', '').strip()

        if not idbook:
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps('El campo "idbook" es requerido y no puede estar vacío.')
            }

        connection = pymysql.connect(host=host, user=user, password=password, db=db)

        try:
            with connection.cursor() as cursor:
                select_query = "SELECT * FROM books WHERE idbook = %s"
                cursor.execute(select_query, (idbook,))
                result = cursor.fetchone()

                if not result:
                    return {
                        'statusCode': 404,
                        'headers': HEADERS,
                        'body': json.dumps('Libro no encontrado')
                    }

                delete_query = "DELETE FROM books WHERE idbook = %s"
                cursor.execute(delete_query, (idbook,))
                connection.commit()

                return {
                    'statusCode': 200,
                    'headers': HEADERS,
                    'body': json.dumps('Libro eliminado exitosamente')
                }

        except Exception as e:
            connection.rollback()
            return {
                'statusCode': 500,
                'headers': HEADERS,
                'body': json.dumps(f'Error al eliminar en la base de datos: {str(e)}')
            }

        finally:
            connection.close()

    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps(f'Error en los datos de entrada: {str(ve)}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error en la petición: {str(e)}')
        }
