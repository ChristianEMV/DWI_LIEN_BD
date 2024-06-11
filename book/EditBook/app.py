import pymysql
import json


host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"


def lambda_handler(event, __):
    request_body = json.loads(event['body'])
    idbook = request_body['idbook']
    titulo = request_body['titulo']
    fecha_publicacion = request_body['fecha_publicacion']
    autor = request_body['autor']
    editorial = request_body['editorial']
    status = request_body['status']

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            update_query = "UPDATE books SET titulo = %s, fecha_publicacion = %s, autor = %s, editorial = %s, status = %s WHERE idbook = %s"
            cursor.execute(update_query, (titulo, fecha_publicacion, autor, editorial, status, idbook))
            if cursor.rowcount == 0:
                response_message = 'Libro no encontrado'
                return {
                    'statusCode': 404,
                    'body': json.dumps(response_message)
                }
        connection.commit()
        response_message = 'Libro actualizado'
        return {
            'statusCode': 200,
            'body': json.dumps(response_message)
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()



