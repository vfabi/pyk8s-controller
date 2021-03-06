import json

from kubernetes import client
from kubernetes.client import V1Endpoints
from kubernetes.client.rest import ApiException


class ElectionRecord(object):

    def __init__(self, raw=None):
        if raw is None:
            raw = {
                "apiVersion": "v1",
                "kind": "Endpoints",
                "metadata": {
                    "annotations": {
                        "control-plane.alpha.kubernetes.io/leader": "",
                    },
                    "name": ""
                }
            }
        self._raw = raw

    def create(self, namespace):
        core_api = client.CoreV1Api()
        self._raw = core_api.create_namespaced_endpoints(namespace, self._raw).to_dict()

    @property
    def name(self):
        return self._raw['metadata']['name']

    @name.setter
    def name(self, value):
        self._raw['metadata']['name'] = value

    @property
    def namespace(self):
        return self._raw['metadata']['namespace']

    @classmethod
    def get(cls, name, namespace, safe=True):
        core_api = client.CoreV1Api()

        # Fix k8 1.9 compatibility
        # Similar issue to https://github.com/kubernetes-client/python/issues/415
        @property
        def subsets(self):
            return self._subsets

        @subsets.setter
        def subsets(self, subsets):
            self._subsets = subsets

        V1Endpoints.subsets = subsets
        try:
            resp = core_api.read_namespaced_endpoints(name, namespace).to_dict()
            if resp is None:
                return None
        except ApiException as e:
            if e.status == 404 and safe:
                return None
            raise
        return cls(resp)

    def update(self):
        core_api = client.CoreV1Api()
        core_api.patch_namespaced_endpoints(self.name, self.namespace, self._raw)

    @property
    def leader_data(self):
        leader_string = self._raw['metadata']['annotations']["control-plane.alpha.kubernetes.io/leader"]
        if leader_string == "":
            return {
                'identity': None,
                'lease_duration': None,
                'acquire_date': None,
                'renew_date': None,
                'leader_transitions': 0
            }
        return json.loads(leader_string)

    @leader_data.setter
    def leader_data(self, value):
        self._raw['metadata']['annotations']["control-plane.alpha.kubernetes.io/leader"] = json.dumps(value)

    @property
    def leader_identity(self):
        return self.leader_data['identity']

    @leader_identity.setter
    def leader_identity(self, value):
        leader_data = self.leader_data
        leader_data['identity'] = value
        self.leader_data = leader_data

    @property
    def lease_duration(self):
        return self.leader_data['lease_duration']

    @lease_duration.setter
    def lease_duration(self, value):
        leader_data = self.leader_data
        leader_data['lease_duration'] = value
        self.leader_data = leader_data

    @property
    def acquire_date(self):
        return self.leader_data['acquire_date']

    @acquire_date.setter
    def acquire_date(self, value):
        leader_data = self.leader_data
        leader_data['acquire_date'] = value
        self.leader_data = leader_data

    @property
    def renew_date(self):
        return self.leader_data['renew_date']

    @renew_date.setter
    def renew_date(self, value):
        leader_data = self.leader_data
        leader_data['renew_date'] = value
        self.leader_data = leader_data

    @property
    def leader_transitions(self):
        return self.leader_data['leader_transitions']

    @leader_transitions.setter
    def leader_transitions(self, value):
        leader_data = self.leader_data
        leader_data['leader_transitions'] = value
        self.leader_data = leader_data
