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
            query = """
            SELECT 
                prestamos.idprestamo,
                prestamos.fecha_inicio,
                prestamos.fecha_fin,
                prestamos.iduser,
                prestamos.idbook,
                books.titulo,
                books.fecha_publicacion,
                books.autor,
                books.editorial,
                books.status,
                books.descripcion,
                books.categoria
            FROM 
                prestamos
            INNER JOIN 
                books ON prestamos.idbook = books.idbook
            """
            cursor.execute(query)
            results = cursor.fetchall()

            prestamos = []
            for result in results:
                prestamo = {
                    'idprestamo': result[0],
                    'fecha_inicio': result[1].isoformat() if isinstance(result[1], date) else result[1],
                    'fecha_fin': result[2].isoformat() if isinstance(result[2], date) else result[2],
                    'iduser': result[3],
                    'idbook': result[4],
                    'titulo': result[5],
                    'fecha_publicacion': result[6].isoformat() if isinstance(result[6], date) else result[6],
                    'autor': result[7],
                    'editorial': result[8],
                    'status': result[9],
                    'descripcion': result[10],
                    'categoria': result[11],
                }
                prestamos.append(prestamo)

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps(prestamos)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps(f'Error al consultar préstamos: {str(e)}')
        }
    finally:
        connection.close()
