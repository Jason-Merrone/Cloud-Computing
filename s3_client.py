import boto3
import logging
import botocore

class S3Client:
    def __init__(self, bucket_name):
        self.logger = logging.getLogger(__name__)
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def get_next_request(self):
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1,
                Prefix='',
                StartAfter=''
            )
            if 'Contents' in response and len(response['Contents']) > 0:
                key = response['Contents'][0]['Key']
                obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                data = obj['Body'].read().decode('utf-8')
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
                self.logger.info(f'Retrieved and deleted request: {key}')
                return key, data
            else:
                return None, None
        except botocore.exceptions.ClientError as e:
            self.logger.error(f'Error accessing S3 bucket: {e}')
            return None, None
