import json
import boto3
from botocore.exceptions import ClientError


HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}


def lambda_handler(event, __):
    client = boto3.client('cognito-idp', region_name='us-east-2')
    client_id = "beona0ds8ott8o8oic3egte6s"
    try:
        body_parameters = json.loads(event["body"])
        username = body_parameters.get('username')
        password = body_parameters.get('password')

        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        print(response)

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        # Obtén los grupos del usuario
        user_groups = client.admin_list_groups_for_user(
            Username=username,
            UserPoolId='us-east-2_Dak0N3NUX'  # Reemplaza con tu User Pool ID
        )

        # Determina el rol basado en el grupo
        role = None
        if user_groups['Groups']:
            role = user_groups['Groups'][0]['GroupName']  # Asumiendo un usuario pertenece a un solo grupo

        return {
            'statusCode': 200,
            'headers': HEADERS,
            'body': json.dumps({
                'id_token': id_token,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': role
            })
        }

    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': HEADERS,
            'body': json.dumps({"error_message": e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({"error_message": str(e)})
        }