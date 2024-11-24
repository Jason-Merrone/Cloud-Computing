import unittest
from unittest.mock import patch, MagicMock
from sqs_client import SQSClient
from request_processor import process_request
from widget_storage import Storage

class TestSQSClient(unittest.TestCase):
    @patch('boto3.client')
    def test_get_queue_url(self, mock_boto3_client):
        mock_sqs = mock_boto3_client.return_value
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'http://mock-queue-url'}

        client = SQSClient('mock-queue')
        self.assertEqual(client.queue_url, 'http://mock-queue-url')

    @patch('boto3.client')
    def test_get_next_request(self, mock_boto3_client):
        mock_sqs = mock_boto3_client.return_value
        mock_sqs.receive_message.return_value = {
            'Messages': [
                {'MessageId': '1', 'ReceiptHandle': 'abc', 'Body': '{"type": "create"}'}
            ]
        }

        client = SQSClient('mock-queue')
        message_id, receipt_handle, body = client.get_next_request()
        self.assertEqual(message_id, '1')
        self.assertEqual(receipt_handle, 'abc')
        self.assertEqual(body, '{"type": "create"}')

    @patch('boto3.client')
    def test_delete_message(self, mock_boto3_client):
        mock_sqs = mock_boto3_client.return_value
        client = SQSClient('mock-queue')
        client.delete_message('mock-receipt-handle')
        mock_sqs.delete_message.assert_called_with(
            QueueUrl=client.queue_url, ReceiptHandle='mock-receipt-handle'
        )


class TestRequestProcessor(unittest.TestCase):
    @patch('request_processor.Storage')
    def test_process_create_request(self, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        data = '{"type": "create", "widgetId": "w123", "owner": "John Doe"}'

        process_request(data, 's3', 'mock-bucket')
        mock_storage.store_widget.assert_called_once()

    @patch('request_processor.Storage')
    def test_process_delete_request(self, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        data = '{"type": "delete", "widgetId": "w123"}'

        process_request(data, 'dynamodb', 'mock-table')
        mock_storage.delete_widget.assert_called_with('w123')

    @patch('request_processor.Storage')
    def test_process_update_request(self, mock_storage_class):
        mock_storage = mock_storage_class.return_value
        data = '{"type": "update", "widgetId": "w123", "owner": "John Doe"}'

        process_request(data, 's3', 'mock-bucket')
        mock_storage.update_widget.assert_called_once()


class TestStorage(unittest.TestCase):
    @patch('boto3.client')
    def test_store_widget_s3(self, mock_boto3_client):
        mock_s3 = mock_boto3_client.return_value
        storage = Storage('s3', 'mock-bucket')
        widget = {'widgetId': 'w123', 'owner': 'John Doe'}
        storage.store_widget(widget)

        mock_s3.put_object.assert_called_once()

    @patch('boto3.resource')
    def test_delete_widget_dynamodb(self, mock_boto3_resource):
        mock_dynamo = mock_boto3_resource.return_value
        mock_table = mock_dynamo.Table.return_value
        storage = Storage('dynamodb', 'mock-table')
        storage.delete_widget('w123')

        mock_table.delete_item.assert_called_with(Key={'id': 'w123'})

if __name__ == '__main__':
    unittest.main()
