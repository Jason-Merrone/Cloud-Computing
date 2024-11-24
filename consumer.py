import time
import logging
from s3_client import S3Client
from sqs_client import SQSClient
from request_processor import process_request
from logger import setup_logging
from argparse import ArgumentParser


def parse_arguments():
    parser = ArgumentParser(description='AWS Consumer Program')
    parser.add_argument('--storage', choices=['s3', 'dynamodb'], required=True, help='Storage strategy')
    parser.add_argument('--resource', required=True, help='Resource identifier (bucket or table name)')
    parser.add_argument('--request-bucket', help='S3 Bucket containing widget requests')
    parser.add_argument('--sqs-queue', help='SQS Queue containing widget requests')
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_arguments()
    logger = logging.getLogger(__name__)
    logger.info('Starting AWS Consumer Program')

    s3_client = S3Client(args.request_bucket) if args.request_bucket else None
    sqs_client = SQSClient(args.sqs_queue) if args.sqs_queue else None

    stop_condition = False

    while not stop_condition:
        data = None
        if s3_client:
            key, data = s3_client.get_next_request()
            if key:
                logger.info(f'Processing request from S3: {key}')

        if not data and sqs_client:
            message_id, receipt_handle, data = sqs_client.get_next_request()
            if message_id:
                logger.info(f'Processing request from SQS: {message_id}')

        if data:
            process_request(data, args.storage, args.resource)
            if receipt_handle:  # Delete the message from SQS after processing
                sqs_client.delete_message(receipt_handle)
        else:
            time.sleep(0.1)


if __name__ == '__main__':
    main()
