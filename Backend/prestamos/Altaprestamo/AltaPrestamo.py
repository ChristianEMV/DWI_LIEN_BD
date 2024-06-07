import json
from Backend.prestamos.Altaprestamo.ConnectionDB import get_connection


def lambda_handler(event):
    request_body = json.loads(event['body'])
    fecha_inicio = request_body['fecha_inicio']
    fecha_fin = request_body['fecha_fin']
    iduser = request_body['iduser']
    idbook = request_body['idbook']

    connection = get_connection()

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
                    'body': json.dumps('Préstamo exitoso')
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps('El libro no está disponible para préstamo')
                }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()
