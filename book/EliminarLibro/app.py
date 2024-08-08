import pymysql
import json


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, __):

    idbook = event.get('pathParameters', {}).get('idbook', '').strip()
    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM books WHERE idbook = %s"
            cursor.execute(select_query, (idbook,))
            result = cursor.fetchone()

            if not result:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
                    },
                    'body': json.dumps('Libro no encontrado')
                }

            delete_query = "DELETE FROM books WHERE idbook = %s"
            cursor.execute(delete_query, (idbook,))
            connection.commit()

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
                },
                'body': json.dumps('Libro eliminado')
            }

    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
            },
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()


