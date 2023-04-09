import boto3  # import Boto3
import botocore


# Creates the Users table. NOTE: SHOULD NOT BE CALLED WHEN ALREADY CREATED.
def create_users_table(aws_access_key_id, aws_secret_access_key, region_name, dynamodb=None):
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name
                              )

    # Table definition
    table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'user_id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'guild_id',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_id',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'guild_id',
                'AttributeType': 'N'
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

    return table


# Adds a new user to Users if not already present.
def add_user(user_id, guild_id, aws_access_key_id, aws_secret_access_key, region_name, dynamodb=None,
             initial_points=1000):
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name
                              )

    table = dynamodb.Table('Users')

    response = table

    try:

        response = table.put_item(
            Item={
                'user_id': user_id,
                'guild_id': guild_id,
                'info': {
                    'user_points': initial_points
                }
            },
            ConditionExpression='attribute_not_exists(user_id) AND attribute_not_exists(guild_id)'
        )

    except botocore.exceptions.ClientError as e:
        # Ignore the ConditionalCheckFailedException, bubble up
        # other exceptions.
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise

    return response
