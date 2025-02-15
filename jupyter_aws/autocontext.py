import os
from enum import Enum
import platform

class Runtime(Enum):
    OTHER = -1
    DOCKER = 1
    KUBERNETES = 2
    MACOS = 3
    WINDOWS = 4
    
def detect_runtime():
    uname = platform.uname()
    if os.path.exists("/var/run/secrets/kubernetes.io") or "KUBERNETES_SERVICE_HOST" in os.environ:
        runtime = Runtime.KUBERNETES
    elif os.path.exists("/.dockerenv"):
        runtime = Runtime.DOCKER
    elif uname.system == 'Darwin':
        runtime = Runtime.MACOS
    elif uname.system == 'Windows':
        runtime = Runtime.WINDOWS
    else:
        runtime = Runtime.OTHER
    return runtime

class Network:
    MITM_CACERT=os.path.expanduser("~/etc/CombinedCA.cer")

    def __init__(self, mitm=True):
        self.mitm = mitm

    def cacert(self):
        if self.mitm:
            return Network.MITM_CACERT
        else:
            import certifi
            return certifi.where()


class Context:
    def __init__(self, backend=None, environment=None, network=None):
        rt = detect_runtime()
        if backend is None:
            if rt == Runtime.KUBERNETES:
                # ARAD Kubernetes containers run in EKS
                from .aws.context import Context as AWSContext
                self.backend = AWSContext()
            
            if rt == Runtime.DOCKER:
                self.backend = TinyServerContext()

            if rt == Runtime.MACOS or rt == Runtime.WINDOWS:
                self.backend = LocalBackend()
        else:
            self.backend = backend
        
        if environment is None:
            self.environment = "dev"
        else:
            self.environment = environment

        if network is None:
            if rt == Runtime.KUBERNETES:
                self.network = Network(mitm=False)
            else:
                self.network = Network(mitm=True)

    @classmethod
    def create(cls, config : str):


