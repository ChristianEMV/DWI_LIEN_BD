import json

from Backend.book.RecuperarLibro.ConnectionDB import get_connection

from datetime import date


def lambda_handler(event):
    request_body = json.loads(event['body'])
    idbook = request_body['idbook']

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM books WHERE idbook = %s"
            cursor.execute(select_query, (idbook,))
            result = cursor.fetchone()

        if result:
            book = {
                'idbook': result[0],
                'titulo': result[1],
                'fecha_publicacion': result[2].isoformat() if isinstance(result[2], date) else result[2],
                'autor': result[3],
                'editorial': result[4],
                'status': result[5],
            }
            return {
                'statusCode': 200,
                'body': json.dumps(book)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Libro no encontrado')
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error al recuperar el libro: {str(e)}')
        }

    finally:
        connection.close()
