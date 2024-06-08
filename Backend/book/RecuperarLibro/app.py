import pymysql
import json


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, __):
    idbook = event['pathParameters'].get('idbook')

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

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
