import boto3
from botocore.exceptions import ClientError
import pymysql
import json
from datetime import date

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}

def get_secret():
    secret_name = "prodLien"
    region_name = "us-east-2"

    # Crea un cliente de Secrets Manager
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
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def lambda_handler(event, __):
    # Recupera las credenciales desde Secrets Manager
    secret = get_secret()

    # Extrae las credenciales del secreto
    host = secret["host"]
    user = secret["username"]
    passw = secret["password"]
    db = secret["db"]

    # Conexión a la base de datos usando las credenciales recuperadas
    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

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

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(books)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps('Error al recuperar los libros: {}'.format(str(e)))
        }

    finally:
        connection.close()