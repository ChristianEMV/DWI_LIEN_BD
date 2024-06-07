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
            print(result)
        if result:

            return {
                'statusCode': 200,
                'body': json.dumps(result)
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
