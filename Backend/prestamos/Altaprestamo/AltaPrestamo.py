import json
from Backend.prestamos.Altaprestamo.ConnectionDB import get_connection


def lambda_handler(event):
    print(event)
    request_body = json.loads(event['body'])
    fechainicio = request_body['fecha_inicio']
    fechafin = request_body['fecha_fin']
    idusuario = request_body['idUsuario']
    idlibro = request_body['idLibro']

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            select_query = "SELECT statusLibro from books where idbook like (%s)"
            cursor.execute(select_query, (idlibro))
        result = cursor.fetchone()
        if result == 0:
            with connection.cursor() as cursor:
                insert_query = "INSERT INTO prestamo (fechaInicio, fechaFinal, Usuarios_idUsuarios, Libros_idLibros)VALUES (%s,%s,%s,%s,%s))"
                cursor.execute(insert_query, (fechainicio, fechafin, idusuario, idlibro))
        connection.commit()
        return {
            'statusCode': 200,
            'body': json.dumps('prestamo exitoso')
        }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps('Error al insertar en la base de datos: {}'.format(str(e)))
        }
    finally:
        connection.close()
