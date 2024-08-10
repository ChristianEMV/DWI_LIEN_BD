import pymysql
import json

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
    print(event)
    request_body = json.loads(event['body'])
    titulo = request_body['titulo']
    fecha_publicacion = request_body['fecha_publicacion']
    autor = request_body['autor']
    editorial = request_body['editorial']
    status = request_body['status']
    descripcion = request_body['descripcion']
    categoria = request_body['categoria']

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO books (titulo, fecha_publicacion, autor, editorial, status,descripcion,categoria) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (titulo, fecha_publicacion, autor, editorial, status, descripcion, categoria))
        connection.commit()
        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps('Libro registado exitosamente')
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()
