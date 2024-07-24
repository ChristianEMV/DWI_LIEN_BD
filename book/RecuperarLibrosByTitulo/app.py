import pymysql
import json
import re
from datetime import date


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, context):
    search_term = event['queryStringParameters'].get('title', '').strip()

    if not search_term:
        return {
            'statusCode': 400,
            'body': json.dumps('Parámetro de búsqueda "title" no proporcionado.')
        }

    search_term_escaped = re.escape(search_term)

    select_query = f"SELECT * FROM books WHERE titulo REGEXP '\\\\b{search_term_escaped}\\\\b'"

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
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

