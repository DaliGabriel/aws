import json
import boto3

dynamodb_client = boto3.resource('dynamodb')
table = dynamodb_client.Table('testTable')

def lambda_handler(event, context):
    
    event=json.loads(event['body'])

    try:
        response=table.put_item(Item=event)
        return table.scan()
    except:
        raise
