from jupyter_aws import Context
from jupyter_aws.errors import ConfigurationError

def test_object_put_get():
    config = {
        "default": {
            "environment": {
                "ENV": "test"
            },
            "backend": {
                "type": "local",
                "basedir": "/tmp/jaws-%ENV%"
            }
        },
        "drivep": {
            "environment": {
                "SERVER": "drivep.ank.com",
            },
            "network": {
                "verify-ssl": False
            },
            "backend": {
                "type": "nas",
                "server": "%SERVER%",
                "webdav-port": 5006
            }
        }
    }
    ctx = Context("default", config)
    myobj = ctx.object("foo/bar/baz")
    myobj.put_text("Hello world!")
    print(myobj.get_text())

def test_object_bad_config():
    config = {
        "default": {
            "backend": {
                "type": "local"
            }
        }
    }
    ctx = Context("default", config)
    expected_exception = False
    try:
        myobj = ctx.object("foo/bar/baz")
        myobj.put_text("Hello world!")
    except ConfigurationError:
        # expected result
        expected_exception = True
    assert(expected_exception)

