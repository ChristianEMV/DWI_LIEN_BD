import pymysql


def get_connection():
    return pymysql.connect(
        host='database-lien.cpu2e8akkntd.us-east-2.rds.amazonaws.com',
        user='admin',
        password='password',
        database='lien'
    )
