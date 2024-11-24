import boto3
import logging
import botocore


class SQSClient:
    def __init__(self, queue_name):
        self.logger = logging.getLogger(__name__)
        self.sqs = boto3.client('sqs')
        self.queue_url = self.get_queue_url(queue_name)

    def get_queue_url(self, queue_name):
        try:
            response = self.sqs.get_queue_url(QueueName=queue_name)
            return response['QueueUrl']
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error retrieving queue URL for {queue_name}: {e}')
            raise

    def get_next_request(self):
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=2
            )
            if 'Messages' in response:
                message = response['Messages'][0]
                receipt_handle = message['ReceiptHandle']
                body = message['Body']
                self.delete_message(receipt_handle)
                return message['MessageId'], body
            return None, None
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error receiving message from SQS: {e}')
            return None, None

    def delete_message(self, receipt_handle):
        try:
            self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)
            self.logger.info('Successfully deleted message from SQS')
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error deleting message from SQS: {e}')
