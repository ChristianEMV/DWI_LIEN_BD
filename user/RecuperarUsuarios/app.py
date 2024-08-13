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
    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM users"
            cursor.execute(select_query)
            results = cursor.fetchall()

            users = []
            for result in results:
                userR = {
                    'iduser': result[0],
                    'nombre': result[1],
                    'email': result[2],
                    'fechanacimiento': result[3].isoformat() if isinstance(result[3], date) else result[3],
                    'phone': result[4],
                    'username': result[5],
                }
                users.append(userR)

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(users)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps('Error al recuperar los usuarios: {}'.format(str(e)))
        }

    finally:
        connection.close()