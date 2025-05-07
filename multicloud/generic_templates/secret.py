import os
from .docker_util import detect_runtime, DockerRuntime
import json
from sys import stderr

JAWS_RUNTIME = os.environ.get("JAWS_RUNTIME", None)

class Secret:
    """Fetches secrets automatically by redirecting the secret request to the 
    appropriate service based on the detected runtime environment
    
    Environment Variables:
        export JAWS_RUNTIME=KUBERNETES
            -- forces the use of the AWS secrets manager
        export JAWS_RUNTIME=DOCKER
            -- forces the use of the secret server for local docker testing
        export JAWS_RUNTIME=OTHER
            -- forces the use of keyring for local MacBook testing
    """

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
        """Fetches AWS secrets"""
        import boto3    
        from botocore.exceptions import ClientError
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name='us-west-2'
        )
        try:
            get_secret_value_response = client.get_secret_value(SecretId=self.name)
            return json.loads(get_secret_value_response['SecretString'])
        except ClientError as e:
            print("ERROR: Unable to get secret {self.name}", file=stderr)
            raise ValueError(f"Unable to get AWS secret {self.name}")

    def get_secret_keyring(self) -> dict:
        try:
            """Fetches localhost secrets from keyring"""
            from keyring import get_password
            return json.loads(get_password("aws", self.name))
        except Exception as e:
            print(f"ERROR: Unable to load keyring entry aws,{self.name}", file=stderr)
            raise ValueError(f"Unable to load keyring entry aws,{self.name}")

    def get_secret_server(self) -> dict:
        try:
            """Fetches localhost secrets from within local docker"""
            import requests
            url = f"http://host.docker.internal:4443/secret/aws/{self.name}"
            r = requests.get(url)
            assert(r.status_code == 200)
            return r.json()
        except Exception as e:
            raise ValueError(f"secret server unable to fetch {self.name}")

