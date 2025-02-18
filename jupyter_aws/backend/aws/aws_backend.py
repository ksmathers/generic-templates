import boto3.session
from ..backend import Backend
from .aws_secret import AwsSecret
from .aws_object import AwsObject
from .aws_options import AwsOptions
from ..secret import Secret
from ..object import Object
import boto3

class AwsBackend(Backend):
    def __init__(self, ctx, region, bucket):
        super().__init__(ctx, "LocalBackend")
        self.bucket = bucket
        self.region = region
        self.session = boto3.session.Session()

    def secret(self, name) -> Secret:
        client = self.session.client(
            service_name='secretsmanager',
            region_name=self.region
        )
        return AwsSecret(self.ctx, self.session, name, client)
    
    def object(self, key) -> Object:
        client = self.session.client(
            service_name='s3',
            region_name=self.region
        )
        return AwsObject(self.ctx, key, self.bucket, client)
    
    def options(self) -> Options:
        return AwsOptions


    