
from copy import deepcopy
import json

from bravado_core.spec import Spec
from bravado.requests_client import RequestsClient

from .request_factory import RequestFactory
from .class_factory import SchemaObjectFactory

__all__ = ['Client']


class Client(object):

    def __init__(self, server_url,
                 origin_spec=None,
                 session=None,
                 remote=None):

        self.server_url = server_url
        self.session = session
        self.remote = remote

        # if an origin_spec is not providing on init, presume that the
        # client has be subclassed to implement the method 'fetch_swagger_spec'

        if not origin_spec:
            origin_spec = self.fetch_swagger_spec()

        self.origin_spec = deepcopy(origin_spec)

        # bravado swagger spec created from the origin_spec, linking
        # the bravado requests session to the AOSpy session

        self.swagger_spec = self.make_swagger_spec()

        # alias for ease-of-use
        self.definitions = self.origin_spec.get('definitions') or {}

        # function to de-reference '$ref' items
        self.deref = self.swagger_spec.deref

        # control if the request response content should be automatically
        # be returned as a modeled object (using the associated schema def)
        # or as-is content from the AOS.  By default set this to as-is.
        # caller can set this to True so that all responses are handled
        # the same; or they can set this on a request-by-request bases
        # in the Request instance.

        self.model_response = False

        # setup request methods to create Request instances for command
        # execution.

        rqst_factory = RequestFactory(self)
        self.request = rqst_factory.attr_factory()
        self.command_request = rqst_factory.command_request
        self.path_requests = rqst_factory.path_requests

        # object to use for building jsonschema classes/instances
        self.build = SchemaObjectFactory(self)

    def fetch_swagger_spec(self):
        raise RuntimeError('fetch_swagger_spec not implemeted')

    def make_swagger_spec(self):
        http_client = RequestsClient()

        # if the caller provided an existing requests session,
        # then use there here.

        if self.session:
            http_client.session = self.session

        return Spec.from_dict(
            spec_dict=self.origin_spec,
            origin_url=self.server_url,
            http_client=http_client,

            # TODO expose these configuration options to the
            # TODO caller; hardcoded for now.  caller could make
            # TODO updates to the self.swagger_spec value

            config={
                'validate_swagger_spec': False,
                'validate_responses': False,
                'use_models': False
            }
        )

    def __repr__(self):
        return json.dumps({
            'client-url': self.server_url
        })
