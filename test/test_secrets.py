from multicloud.autocontext import Context
import random

def test_secret():
    config = {
        "default": {
            "backend": {
                "type": "local"
            }
        }
    }
    ctx = Context('default', config)
    print(ctx)
    slogin = ctx.secret('secret')
    orig_secret = {"randomkey": random.randint(0,1000000) }
    slogin.set(orig_secret)

    slogin2 = ctx.secret('secret')
    read_secret = slogin.get()

    assert(orig_secret == read_secret)


if __name__ == "__main__":
    test_secret()
