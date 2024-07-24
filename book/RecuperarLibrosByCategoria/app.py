import pymysql
import json
from datetime import date


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, __):
    category = event['queryStringParameters'].get('category')

    if not category:
        return {
            'statusCode': 400,
            'body': json.dumps('Parámetro de categoría requerido.')
        }

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM books WHERE categoria = %s"
            cursor.execute(select_query, (category,))
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
                    'categoria': result[7]
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
