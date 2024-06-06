import pymysql


def get_connection():
    return pymysql.connect(
        host='db-test-aws.cluster-c5imkqe0kzta.us-east-2.rds.amazonaws.com',
        user='admin',
        password='password',
        database='dbTest'
    )
