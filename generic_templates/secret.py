import os
from .docker_util import detect_runtime, DockerRuntime
import json

JAWS_RUNTIME = os.environ.get("JAWS_RUNTIME", None)

class Secret:
    """Fetches secrets automatically by redirecting the secret request to the 
    appropriate service based on the detected runtime environment"""

    def __init__(self, name : str, system : str = JAWS_RUNTIME):
        if system is None:
            system = detect_runtime()
        else:
            system = DockerRuntime[system]
        self.system = system
        self.name = name

    def get_secret(self) -> dict:
        if self.system == DockerRuntime.KUBERNETES:
            return self.get_secret_aws()
        elif self.system == DockerRuntime.OTHER:
            return self.get_secret_keyring()
        elif self.system == DockerRuntime.DOCKER:
            return self.get_secret_server()
        else:
            raise NotImplementedError(f"Unknown secret system: {self.system}")
    
    def get_secret_aws(self) -> dict:
        """Fetches AWS secrets from EKS"""
        raise NotImplementedError("get_secret_aws() not implemented")

    def get_secret_keyring(self) -> dict:
        """Fetches localhost secrets from keyring"""
        from keyring import get_password
        return json.loads(get_password("aws", self.name))

    def get_secret_server(self) -> dict:
        """Fetches localhost secrets from within local docker"""
        import requests
        url = f"http://host.docker.internal:4443/secret/aws/{self.name}"
        r = requests.get(url)
        assert(r.status_code == 200)
        return r.json()

