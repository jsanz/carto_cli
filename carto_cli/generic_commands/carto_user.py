from carto.exceptions import CartoException
from carto.sql import SQLClient
from carto.auth import APIKeyAuthClient


class CARTOUser(object):

    def __init__(self, user_name=None, org_name=None,
                 api_url=None, api_key=None):
        self.user_name = user_name
        self.org_name = org_name
        self.api_url = api_url
        self.api_key = api_key

    def initialize(self):
        if not self.api_url and self.user_name:
            self.api_url = "https://{}.carto.com/api/".format(self.user_name)
        elif not self.api_url and not self.user_name:
            raise Exception(
                'Not enough data provided to initialize the client')

        if self.org_name:
            self.client = APIKeyAuthClient(
                self.api_url, self.api_key, self.org_name)
        else:
            self.client = APIKeyAuthClient(self.api_url, self.api_key)

        self.sql_client = SQLClient(self.client)

    def execute_sql(self, query, parse_json=True, format=None, do_post=False):
        try:
            try:
                self.client
            except AttributeError:
                self.initialize()
            return self.sql_client.send(query, parse_json=parse_json,
                                        format=format, do_post=do_post)
        except CartoException as e:
            raise Exception(e.args[0].args[0][0])
