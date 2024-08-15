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


def lambda_handler(event, __):
    try:
        secret = get_secret()
        host = secret.get("host")
        user = secret.get("username")
        password = secret.get("password")
        db = secret.get("dbInstanceIdentifier")

        if not all([host, user, password, db]):
            raise ValueError("Faltan uno o más parámetros requeridos en el secreto")

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al obtener las credenciales: {str(e)}')
        }

    try:
        request_body = json.loads(event['body'])

        required_fields = ['titulo', 'fecha_publicacion', 'autor', 'editorial', 'status', 'descripcion', 'categoria']
        for field in required_fields:
            if not request_body.get(field):
                raise ValueError(f'El campo "{field}" es requerido y no puede estar vacío.')

        titulo = request_body['titulo']
        fecha_publicacion = request_body['fecha_publicacion']
        autor = request_body['autor']
        editorial = request_body['editorial']
        status = request_body['status']
        descripcion = request_body['descripcion']
        categoria = request_body['categoria']

    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps(f'Error en los datos de entrada: {str(ve)}')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps(f'Error al procesar la solicitud: {str(e)}')
        }

    connection = pymysql.connect(host=host, user=user, password=password, db=db)

    try:
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO books (titulo, fecha_publicacion, autor, editorial, status, descripcion, categoria) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (titulo, fecha_publicacion, autor, editorial, status, descripcion, categoria))
        connection.commit()
        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps('Libro registrado exitosamente')
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

