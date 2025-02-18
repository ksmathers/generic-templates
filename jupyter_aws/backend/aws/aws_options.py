from enum import Enum
from typing import Optional

class S3Sse(Enum):
    #ServerSideEncryption='AES256'|'aws:kms'|'aws:kms:dsse',
    AES256 = "AES256"
    KMS = "aws:kms"
    KMS_DSSE = "aws:kms:dsse"

class S3Payer(Enum):
    REQUESTER = "requester"

class AwsOptions:
    ServerSideEncryption : Optional[S3Sse] = None
    RequestPayer : Optional[S3Payer] = None

    @classmethod
    def populate(cls, opts):
        dd = {}
        for opt in opts:
            v = cls.__getattribute__(cls, opt)
            if v is not None:
                dd[opt] = v.value
        return dd

    @classmethod
    def s3args_put_object(cls):     
        put_object_opts = ['ServerSideEncryption', 'RequestPayer']
        return cls.populate(put_object_opts)
