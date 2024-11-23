import boto3
import logging
import json
import botocore

class Storage:
    def __init__(self, strategy, resource_name):
        self.logger = logging.getLogger(__name__)
        self.strategy = strategy
        self.resource_name = resource_name
        if self.strategy == 's3':
            self.s3 = boto3.client('s3')
        elif self.strategy == 'dynamodb':
            self.dynamodb = boto3.resource('dynamodb')
        else:
            self.logger.error('Invalid storage strategy')

    def store_widget(self, widget):
        if self.strategy == 's3':
            self.store_in_s3(widget)
        elif self.strategy == 'dynamodb':
            self.store_in_dynamodb(widget)
        else:
            self.logger.error('Invalid storage strategy')

    def store_in_s3(self, widget):
        owner = widget['owner'].replace(' ', '-').lower()
        key = f"widgets/{owner}/{widget['widgetId']}"
        data = json.dumps(widget)
        try:
            self.s3.put_object(Bucket=self.resource_name, Key=key, Body=data)
            self.logger.info(f'Widget stored in S3 with key: {key}')
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error storing widget in S3: {e}')

    def store_in_dynamodb(self, widget):
        try:
            table = self.dynamodb.Table(self.resource_name)
            table.put_item(Item=widget)
            self.logger.info(f'Widget stored in DynamoDB table: {self.resource_name}')
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error storing widget in DynamoDB: {e}')