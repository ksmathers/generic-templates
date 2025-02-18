from .common.runtime import Runtime, detect_runtime
from .backend import Backend
from .common.network import Network
from .common.environment import Environment
import os


def create_backend(ctx, backend : dict) -> Backend:
    if backend is None:
        rt = detect_runtime()
        if rt == Runtime.KUBERNETES:
            backend = { "type": "aws", "creds": "auto" }
        elif rt == Runtime.DOCKER:
            backend = { "type": "tinyserver" }
        elif rt == Runtime.MACOS or rt == Runtime.WINDOWS:
            backend = { "type": "local", "basedir": "/tmp" }
        else:
            raise NotImplementedError(f"Unable to create backend for {rt}")
    
    assert('type' in backend)
    if backend['type'] == 'aws':
        from .backend.aws.aws_backend import AwsBackend
        return AwsBackend(ctx, backend['creds'])
    elif backend['type'] == 'tinyserver':
        from .backend.tiny.tiny_backend import TinyBackend
        return TinyBackend(ctx)
    elif backend['type'] == 'local':
        from .backend.local.local_backend import LocalBackend
        return LocalBackend(ctx, backend.get('basedir'))


def create_network(ctx, network : dict) -> Network:
    if network is None:
        import certifi
        rt = detect_runtime()
        if rt == Runtime.KUBERNETES:
            network = { "cacerts": certifi.where() }
        elif rt == Runtime.DOCKER:
            network = { "cacerts": certifi.where() }
        elif rt == Runtime.MACOS:
            network = { "cacerts": "~/etc/CombinedCA.cer" }
        else:
            raise NotImplementedError(f"Unable to create network for {rt}")
    return Network(ctx, network)

def create_environment(ctx, environment : dict) -> Environment:
    if environment is None:
        environment = os.environ
    return Environment(ctx, environment)