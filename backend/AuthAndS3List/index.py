import boto3
import os
import json

# Check a dynamodb table to see if a username + password combo is valid


def check_user(username, password):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    response = table.get_item(
        Key={
            'username': username,
            'password': password
        }
    )
    return response.get('Item') is not None

# List the objects in an S3 bucket


def list_s3(bucketName):
    AWS_ACCESS_KEY_ID = 'ASIAIOSFODNN7EXAMPLE'
    AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE'

    client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    object_keys = []
    continuation_token = None

    while True:
        if continuation_token:
            response = client.list_objects(
                Bucket=bucketName, ContinuationToken=continuation_token)
        else:
            response = client.list_objects(Bucket=bucketName)

        for content in response.get('Contents', []):
            object_keys.append(content['Key'])

        if response['IsTruncated']:
            continuation_token = response['NextContinuationToken']
        else:
            break

    return json.dumps(object_keys)


def lambda_handler(event, context):
    body = event.get('body')
    if body:
        data = json.loads(body)
        operation = data.get('operation')

    if operation == 'validate_user':
        username = data.get('username')
        password = data.get('password')
        response = check_user(username, password)
    elif operation == 'list_s3':
        bucket_name = os.environ.get('BUCKET_NAME')
        response = list_s3(bucket_name)

    else:
        return {
            'statusCode': 400,
            'body': 'Invalid operation warning',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            }
        }
    return {
        'statusCode': 200,
        'body': response,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        }
    }
