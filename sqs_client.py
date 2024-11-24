import boto3
import logging
import botocore


class SQSClient:
    def __init__(self, queue_name):
        self.logger = logging.getLogger(__name__)
        self.sqs = boto3.client('sqs')
        self.queue_url = self.get_queue_url(queue_name)
        self.cached_messages = []  # Cache for received messages

    def get_queue_url(self, queue_name):
        try:
            response = self.sqs.get_queue_url(QueueName=queue_name)
            return response['QueueUrl']
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error retrieving queue URL for {queue_name}: {e}')
            raise

    def get_next_request(self):
        if self.cached_messages:
            message = self.cached_messages.pop(0)
            return message['MessageId'], message['ReceiptHandle'], message['Body']

        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=2
            )
            if 'Messages' in response:
                self.cached_messages = response['Messages']  # Cache messages
                return self.get_next_request()  # Return the first message
            return None, None, None
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error receiving message from SQS: {e}')
            return None, None, None

    def delete_message(self, receipt_handle):
        try:
            self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
            self.logger.info('Successfully deleted message from SQS')
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error deleting message from SQS: {e}')
