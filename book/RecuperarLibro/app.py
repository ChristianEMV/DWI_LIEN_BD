import json
import pymysql
import jwt
from datetime import date

host = "database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com"
user = "admin"
passw = "password"
db = "lien"

# JWKS (JSON Web Key Set) con las claves públicas
jwks = {
    "keys": [
        {
            "alg": "RS256",
            "e": "AQAB",
            "kid": "qxeicpvaM7hE+8wktwB+68eFfm03UPOmkOHLsAx8/o4=",
            "kty": "RSA",
            "n": "rj9MKDgGfyDTIp1b2zvwaGVFPDAxmK4GURS7d9HVElhhMdwRfnO1oVq4iIMjlNTVOYOCJwVjdnuYSf-gkNUWBR4k-ZeUe_cMvPKl5rXPk4n3b9f2tMKhpmGKDKTODxjkBbnSQvHSSP2U7Lge6vDb9Zn72B7cA-Yq3lrGr7zNcf7t0PqA0dj_rnolEs5RlFYeadPPNJVgrOgX-pzyZgX_DWLaaiyoO0aD7x5lKDuRgQCOPjxV2GzEiwqK-DGYdmJGN0-npXYamoQbittZeZ0Bz8dC-OS1PFtaIw9qruNbB4Q07QxZESXNcPwheD2elQYvcnedke0lTLDlXzPIzIzs7Q",
            "use": "sig"
        },
        {
            "alg": "RS256",
            "e": "AQAB",
            "kid": "dfa8WTW2xvBHcMXpPXigQpA7BKb7A2jMPMfIkt0h1yw=",
            "kty": "RSA",
            "n": "mHunT7ZQECj1boesotJN9eMX2xDhVZrfuRXY361L7qT_xzmi55X52YxNDlXFCeDqJUmddpbd_NxLMcw6UY3jnDPONzC2aBj2NvhYVNLuPVF-CdH8Zd5CUalTZp2t7h0CeLueaOHYYzF4Zkts1H3GOAeG1Pz5iw2wyVajpPDgBA2K9zEvdhEC2jLE-FsYFEfjNZu4GvjdwzoQG2dR86xTCFrtQsbMD2ZuN4LKU2eytv_7Jdt5aMafjUWpHNHiEBi_-hOnfiESoEPpwu-jsd_pCFmh1nrO1-fNGuQv_g8K-SRat8GDs4t535Qc_kMn1_6HDmRvFiYGb60lvSr4hQTSww",
            "use": "sig"
        }
    ]
}


def get_public_key(kid):
    # Encuentra la clave correspondiente al kid
    for key in jwks['keys']:
        if key['kid'] == kid:
            # Construye la clave pública en formato PEM
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    return None


def lambda_handler(event, context):
    print("------------")
    print(event)
    print("-")

    # Extrae el token JWT del encabezado Authorization
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {
            'statusCode': 401,
            'body': json.dumps('Token JWT no proporcionado o formato incorrecto')
        }

    token = auth_header.split(' ')[1]

    try:
        # Decodifica el token para obtener el kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not kid:
            return {
                'statusCode': 401,
                'body': json.dumps('No se pudo encontrar el kid en el encabezado del token')
            }

        # Obtiene la clave pública correspondiente al kid
        public_key = get_public_key(kid)

        if not public_key:
            return {
                'statusCode': 401,
                'body': json.dumps('Clave pública no encontrada para el kid')
            }

        # Verifica y decodifica el token
        decoded_token = jwt.decode(token, public_key, algorithms=['RS256'])

        # Obtiene los grupos de usuarios de Cognito (roles) desde las claims del token JWT
        user_groups = decoded_token.get('cognito:groups', [])

        # Valida que el usuario pertenece al grupo de administradores
        if 'admin' not in user_groups:
            return {
                'statusCode': 403,
                'body': json.dumps('Acceso denegado. Solo los administradores pueden realizar esta acción.')
            }

        idbook = event.get('pathParameters', {}).get('idbook', '').strip()

        connection = pymysql.connect(host=host, user=user, password=passw, db=db)

        try:
            with connection.cursor() as cursor:
                select_query = "SELECT * FROM books WHERE idbook = %s"
                cursor.execute(select_query, (idbook,))
                result = cursor.fetchone()

            if result:
                book_data = {
                    'idbook': result[0],
                    'titulo': result[1],
                    'fecha_publicacion': result[2].isoformat() if isinstance(result[2], date) else result[2],
                    'autor': result[3],
                    'editorial': result[4],
                    'status': result[5],
                    'descripcion': result[6],
                    'categoria': result[7]
                }

                return {
                    'statusCode': 200,
                    'body': json.dumps(book_data)
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

    except jwt.ExpiredSignatureError:
        return {
            'statusCode': 401,
            'body': json.dumps('Token expirado')
        }
    except jwt.InvalidTokenError:
        return {
            'statusCode': 401,
            'body': json.dumps('Token inválido')
        }

