import os
import certifi

class Network:

    def __init__(self, ctx, network : dict):
        self.ctx = ctx
        self.cacerts = certifi.where()
        if network and 'cacerts' in network:
            self.cacert = os.path.expanduser(network['cacerts'])
        else:
            self.cacert = certifi.where()
        
    def __repr__(self):
        return f'Network<{self.cacert}>'
