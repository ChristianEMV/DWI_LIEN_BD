import pymysql
import json

rds_host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
rds_user = "admin"
rds_password = "password"
rds_db = "lien"


def lambda_handler(event, __):
    connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, db=rds_db)
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
                    'autor': result[3],
                    'editorial': result[4],
                    'status': result[5],
                }
                books.append(book)

            return {
                'statusCode': 200,
                'body': json.dumps(books)
            }

    finally:
        connection.close()