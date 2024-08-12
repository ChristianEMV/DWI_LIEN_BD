import pymysql
import json

host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}


def lambda_handler(event, __):
    request_body = json.loads(event['body'])
    idprestamo = request_body['idprestamo']
    idbook = request_body['idbook']

    if not all([idprestamo, idbook]):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Faltan parámetros de entrada"})
        }

    connection = pymysql.connect(host=host, user=user, password=passw, db=db)

    try:
        with connection.cursor() as cursor:
            delete_query = "DELETE FROM prestamos WHERE idprestamo = %s"
            cursor.execute(delete_query, (idprestamo,))

            update_query = "UPDATE books SET status = '0' WHERE idbook = %s"
            cursor.execute(update_query, (idbook,))

            connection.commit()
            return {
                'statusCode': 200,
                'headers': HEADERS,
                'body': json.dumps('Préstamo eliminado y estatus del libro actualizado')
            }
    except Exception as e:
        connection.rollback()
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps('Error al procesar la devolución: {}'.format(str(e)))
        }
    finally:
        connection.close()
