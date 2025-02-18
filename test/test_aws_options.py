from jupyter_aws.backend.aws.aws_options import AwsOptions, S3Sse, S3Payer

g_put_object_arglist = None
def put_object_impl(**kwargs):
    global g_put_object_arglist
    g_put_object_arglist = kwargs  


class Foo:
    options = AwsOptions

    def __init__(self):
        pass

    def put_object(self, key, value):
        put_object_impl(
            key=key,
            value=value,
            **self.options.s3args_put_object())

def test_put_object_options():
    global g_put_object_arglist
    foo = Foo()
    foo.put_object("mykey", "myvalue")
    assert(g_put_object_arglist == {
        'key': 'mykey', 
        'value': 'myvalue'
    })    
    foo.options.RequestPayer = S3Payer.REQUESTER
    foo.options.ServerSideEncryption = S3Sse.KMS
    foo.put_object("path/to/myobject", "this is a test")
    assert(g_put_object_arglist == {
        'key': 'path/to/myobject', 
        'value': 'this is a test', 
        'ServerSideEncryption': 'aws:kms', 
        'RequestPayer': 'requester'
    })

if __name__ == "__main__":
    test_put_object_options()