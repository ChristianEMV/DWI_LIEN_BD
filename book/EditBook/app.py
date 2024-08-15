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
    'Access-Control-Allow-Methods': 'PUT, OPTIONS'
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

        user_groups = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('cognito:groups', [])

        if 'admin' not in user_groups:
            return {
                'statusCode': 403,
                'headers': HEADERS,
                'body': json.dumps('Acceso denegado. Solo los administradores pueden realizar esta acción.')
            }

        request_body = json.loads(event['body'])
        idbook = request_body.get('idbook')
        titulo = request_body.get('titulo')
        fecha_publicacion = request_body.get('fecha_publicacion')
        autor = request_body.get('autor')
        editorial = request_body.get('editorial')
        status = request_body.get('status')
        descripcion = request_body.get('descripcion')
        categoria = request_body.get('categoria')

        required_fields = ['idbook', 'titulo', 'fecha_publicacion', 'autor', 'editorial', 'status', 'descripcion', 'categoria']
        for field in required_fields:
            if not request_body.get(field):
                raise ValueError(f'El campo "{field}" es requerido y no puede estar vacío.')

        connection = pymysql.connect(host=host, user=user, password=password, db=db)

        try:
            with connection.cursor() as cursor:
                update_query = """
                    UPDATE books 
                    SET titulo = %s, fecha_publicacion = %s, autor = %s, editorial = %s, status = %s, descripcion = %s, categoria = %s 
                    WHERE idbook = %s
                """
                cursor.execute(update_query, (titulo, fecha_publicacion, autor, editorial, status, descripcion, categoria, idbook))

                if cursor.rowcount == 0:
                    response_message = 'Libro no encontrado'
                    return {
                        'statusCode': 404,
                        'headers': HEADERS,
                        'body': json.dumps(response_message)
                    }

            connection.commit()
            response_message = 'Libro actualizado exitosamente'
            return {
                'statusCode': 200,
                'headers': HEADERS,
                'body': json.dumps(response_message)
            }

        except Exception as e:
            connection.rollback()
            return {
                'statusCode': 500,
                'headers': HEADERS,
                'body': json.dumps(f'Error al actualizar en la base de datos: {str(e)}')
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