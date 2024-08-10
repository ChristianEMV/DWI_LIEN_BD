import pymysql
import json


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, __):
    request_body = json.loads(event['body'])
    fecha_inicio = request_body['fecha_inicio']
    fecha_fin = request_body['fecha_fin']
    iduser = request_body['iduser']
    idbook = request_body['idbook']

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT status FROM books WHERE idbook = %s"
            cursor.execute(select_query, (idbook,))
            result = cursor.fetchone()

            if result and result[0] == "0":

                insert_query = "INSERT INTO prestamos (fecha_inicio, fecha_fin, iduser, idbook) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (fecha_inicio, fecha_fin, iduser, idbook))
                connection.commit()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS'
                    },
                    'body': json.dumps('Préstamo exitoso')
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                        'Access-Control-Allow-Methods': 'POST, OPTIONS'
                    },
                    'body': json.dumps('El libro no está disponible para préstamo')
                }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()
