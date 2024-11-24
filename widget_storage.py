import boto3
import logging
import json
import botocore
import datetime

class Storage:
    def __init__(self, strategy, resource_name):
        self.logger = logging.getLogger(__name__)
        self.strategy = strategy
        self.resource_name = resource_name
        if self.strategy == 's3':
            self.s3 = boto3.client('s3')
            self.bucket_name = resource_name
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
        key = f"widgets/{owner}/{widget['widgetId']}.json"
        data = json.dumps(widget)
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType='application/json'
            )
            self.logger.info(f"Successfully stored widget {widget['widgetId']} in S3 at key {key}")
        except Exception as e:
            self.logger.error(f"Failed to store widget {widget['widgetId']} in S3: {e}")

    def store_in_dynamodb(self, widget):
        dynamo_item = {
            'id': widget['widgetId'],  # Primary key
            'owner': widget['owner'],
            'label': widget.get('label', None),
            'description': widget.get('description', None),
            'last_modified_on': widget.get('last_modified_on', datetime.datetime.utcnow().isoformat())
        }

        if 'otherAttributes' in widget:
            for attr in widget['otherAttributes']:
                name = attr['name']
                value = attr['value']
                dynamo_item[name] = value

        try:
            table = self.dynamodb.Table(self.resource_name)
            table.put_item(Item=dynamo_item)
            self.logger.info(f"Widget stored in DynamoDB table: {self.resource_name}")
        except botocore.exceptions.ClientError as e:
            self.logger.error(f"Error storing widget in DynamoDB: {e}")

    def delete_widget(self, widget_id):
        if self.strategy == 's3':
            key = f"widgets/{widget_id}.json"
            try:
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
                self.logger.info(f'Successfully deleted widget {widget_id} from S3.')
            except botocore.exceptions.ClientError as e:
                self.logger.error(f'Error deleting widget from S3: {e}')
        elif self.strategy == 'dynamodb':
            try:
                table = self.dynamodb.Table(self.resource_name)
                table.delete_item(Key={'id': widget_id})
                self.logger.info(f'Successfully deleted widget {widget_id} from DynamoDB.')
            except botocore.exceptions.ClientError as e:
                self.logger.error(f'Error deleting widget from DynamoDB: {e}')

    def update_widget(self, widget):
        self.store_widget(widget)  # Overwrite existing widget

        # Updating in DynamoDB
        if self.strategy == 'dynamodb':
            self.store_in_dynamodb(widget)
