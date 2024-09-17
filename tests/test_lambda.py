import json
import os
import pytest
import boto3
import sys
from unittest.mock import patch
from moto import mock_dynamodb2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import lambda_handler  # Adjust import based on your file structure

@pytest.fixture
def setup_environment():
    # Set up the environment variable for DynamoDB table name
    os.environ['DDB_TABLE'] = 'test-table'
    yield
    del os.environ['DDB_TABLE']

@mock_dynamodb2
def test_lambda_handler_with_payload(setup_environment):
    # Set up mock DynamoDB
    dynamodb = boto3.client('dynamodb', region_name='us-west-2')
    dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {'AttributeName': 'year', 'KeyType': 'HASH'},
            {'AttributeName': 'title', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'year', 'AttributeType': 'N'},
            {'AttributeName': 'title', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # Define the event and context
    event = {
        "body": json.dumps({"year": 2024, "title": "The New Era"})
    }
    context = {}

    # Invoke the Lambda function
    response = lambda_handler(event, context)

    # Verify the response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == "Successfully inserted data!"

    # Verify that the item was inserted into DynamoDB
    result = dynamodb.scan(TableName='test-table')
    items = result['Items']
    assert len(items) == 1
    assert items[0] == {
        'year': {'N': '2024'},
        'title': {'S': 'The New Era'}
    }

@mock_dynamodb2
def test_lambda_handler_without_payload(setup_environment):
    # Set up mock DynamoDB
    dynamodb = boto3.client('dynamodb', region_name='us-west-2')
    dynamodb.create_table(
        TableName='test-table',
        KeySchema=[
            {'AttributeName': 'year', 'KeyType': 'HASH'},
            {'AttributeName': 'title', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'year', 'AttributeType': 'N'},
            {'AttributeName': 'title', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    # Define the event and context
    event = {
        "body": None
    }
    context = {}

    # Invoke the Lambda function
    response = lambda_handler(event, context)

    # Verify the response
    assert response['statusCode'] == 200
    assert json.loads(response['body'])['message'] == "Successfully inserted data!"

    # Verify that the item was inserted into DynamoDB
    result = dynamodb.scan(TableName='test-table')
    items = result['Items']
    assert len(items) == 1
    assert items[0] == {
        'year': {'N': '2012'},
        'title': {'S': 'The Amazing Spider-Man 2'}
    }
