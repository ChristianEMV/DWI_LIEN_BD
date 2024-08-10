import pymysql
import json

from datetime import date

host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}


def lambda_handler(event, __):
    order = event['queryStringParameters'].get('order', 'asc')

    if order not in ['asc', 'desc']:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps('Parámetro de orden inválido. Use "asc" o "desc".')
        }

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = f"SELECT * FROM books ORDER BY fecha_publicacion {order}"
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
            'headers': HEADERS,
            'body': json.dumps('Error al recuperar los libros: {}'.format(str(e)))
        }

    finally:
        connection.close()