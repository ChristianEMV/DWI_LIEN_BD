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

        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'message': 'Cuerpo de la solicitud vacío'})
            }

        request_body = json.loads(event['body'])
        fecha_inicio = request_body.get('fecha_inicio')
        fecha_fin = request_body.get('fecha_fin')
        iduser = request_body.get('iduser')
        idbook = request_body.get('idbook')

        if not all([fecha_inicio, fecha_fin, idbook, iduser]):
            return {
                'statusCode': 400,
                'headers': HEADERS,
                'body': json.dumps({'message': 'Faltan parámetros de entrada'})
            }

        connection = pymysql.connect(host=host, user=user, password=password, db=db)

        try:
            with connection.cursor() as cursor:
                select_query = "SELECT status FROM books WHERE idbook = %s"
                cursor.execute(select_query, (idbook,))
                result = cursor.fetchone()

                if result and result[0] == 0:
                    insert_query = "INSERT INTO prestamos (fecha_inicio, fecha_fin, iduser, idbook) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_query, (fecha_inicio, fecha_fin, iduser, idbook))

                    update_query = "UPDATE books SET status = '1' WHERE idbook = %s"
                    cursor.execute(update_query, (idbook,))

                    connection.commit()
                    return {
                        'statusCode': 200,
                        'headers': HEADERS,
                        'body': json.dumps('Préstamo exitoso y estatus del libro actualizado')
                    }
                else:
                    return {
                        'statusCode': 400,
                        'headers': HEADERS,
                        'body': json.dumps('El libro no está disponible para préstamo')
                    }
        except Exception as e:
            connection.rollback()
            return {
                'statusCode': 500,
                'headers': HEADERS,
                'body': json.dumps(f'Error al insertar en la base de datos: {str(e)}')
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