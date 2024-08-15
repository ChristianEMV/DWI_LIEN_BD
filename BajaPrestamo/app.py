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
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

def lambda_handler(event, context):
    try:
        secret = get_secret()
        host = secret.get("host")
        user = secret.get("username")
        password = secret.get("password")
        db = secret.get("dbInstanceIdentifier")

        if not all([host, user, password, db]):
            raise ValueError("Faltan uno o más parámetros requeridos en el secreto.")

        user_groups = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('cognito:groups', [])

        if 'admin' not in user_groups:
            return {
                'statusCode': 403,
                'headers': HEADERS,
                'body': json.dumps('Acceso denegado. Solo los administradores pueden realizar esta acción.')
            }

        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'message': 'Cuerpo de la solicitud vacío'})
            }

        request_body = json.loads(event['body'])
        idprestamo = request_body.get('idprestamo')
        idbook = request_body.get('idbook')

        if not all([idprestamo, idbook]):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'message': 'Faltan parámetros de entrada'})
            }

        connection = pymysql.connect(host=host, user=user, password=password, db=db)

        try:
            with connection.cursor() as cursor:
                delete_query = "DELETE FROM prestamos WHERE idprestamo = %s"
                cursor.execute(delete_query, (idprestamo,))

                update_query = "UPDATE books SET status = '0' WHERE idbook = %s"
                cursor.execute(update_query, (idbook,))

                connection.commit()
                return {
                    'statusCode': 200,
                    'headers': HEADERS,
                    'body': json.dumps('Préstamo eliminado y estatus del libro actualizado')
                }
        except Exception as e:
            connection.rollback()
            return {
                'statusCode': 500,
                'headers': HEADERS,
                'body': json.dumps('Error al procesar la devolución: {}'.format(str(e)))
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
            'body': json.dumps(f'Error desconocido: {str(e)}')
        }