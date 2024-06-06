import json

from Backend.book.AltaBook.ConnectionDB import get_connection


def lambda_handler(event):
    print(event)
    request_body = json.loads(event['body'])
    titulo = request_body['titulo']
    fecha_publicacion = request_body['fecha_publicacion']
    autor = request_body['autor']
    editorial = request_body['editorial']
    status = request_body['status']

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO books (titulo, fecha_publicacion, autor, editorial, status) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (titulo, fecha_publicacion, autor, editorial, status))
        connection.commit()
        return {
            'statusCode': 200,
            'body': json.dumps('Libro registado exitosamente')
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()
