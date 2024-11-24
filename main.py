import time
import logging
from s3_client import S3Client
from request_processor import process_request
from widget_storage import Storage
from logger import setup_logging
from argparse import ArgumentParser

def parse_arguments():
    parser = ArgumentParser(description='AWS Consumer Program')
    parser.add_argument('--storage', choices=['s3', 'dynamodb'], required=True, help='Storage strategy')
    parser.add_argument('--resource', required=True, help='Resource identifier (bucket or table name)')
    parser.add_argument('--request-bucket', help='Bucket containing widget requests')
    parser.add_argument('--queue-name', help='SQS queue name for widget requests')
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_arguments()
    logger = logging.getLogger(__name__)
    logger.info('Starting AWS Consumer Program')

    s3_client = S3Client(args.request_bucket)
    stop_condition = False

    while not stop_condition:
        key, data = s3_client.get_next_request()
        if data:
            logger.info(f'Processing request: {key}')
            process_request(data, args.storage, args.resource)
        else:
            time.sleep(0.1)

if __name__ == '__main__':
    main()