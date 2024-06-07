import json

from Backend.book.RecupearLibros.ConnectionDB import get_connection

from datetime import date


def lambda_handler():
    connection = get_connection()

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

                }
                books.append(book)

        return {
            'statusCode': 200,
            'body': json.dumps(books)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error al recuperar los libros: {}'.format(str(e)))
        }

    finally:
        connection.close()
