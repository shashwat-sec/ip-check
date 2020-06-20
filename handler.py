import json
import requests
import boto3
import urllib.parse
from netaddr import IPSet
import hmac
import hashlib
import os


def auth(event, context):
    sns = boto3.client('sns')
    body = event['body']
    timestamp = event['headers']['X-Slack-Request-Timestamp']
    concat_message = ('v0:' + timestamp + ':' + body).encode()
    slack_signature = event['headers']['X-Slack-Signature']
    key = (os.environ['slack_secret']).encode()
    hashed_msg = 'v0=' + \
        hmac.new(key, concat_message, hashlib.sha256).hexdigest()
    print(hashed_msg)
    if (hashed_msg != slack_signature):
        return{
            'statusCode': 404,
            'body': json.dumps("Un-Authorized")
        }
    text = "Working on your request..."
    command = body.split("text=")[1]
    command_send = urllib.parse.unquote(command.split("&")[0])
    try:
        ip = IPSet()
        ip.add(command_send)
    except Exception:
        return{
            'statusCode': 200,
            'body': json.dumps("Please enter a valid IP or CIDR")
        }
    response = body.split("response_url=")[1]
    response_url = response.split("&")[0]
    decoded = urllib.parse.unquote(response_url)
    slack_response = sns.publish(
        # Add your aws account id below
        TopicArn='arn:aws:sns:us-east-1:{Your AWS Account ID}:processing-topic',
        Message=decoded+"-"+command_send,
    )
    print(slack_response)
    return {
        'statusCode': 200,
        'body': json.dumps(text)
    }
