from carto.exceptions import CartoException
from carto.sql import SQLClient
from carto.sql import BatchSQLClient
from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from carto.sync_tables import SyncTableJobManager

import warnings
import requests
import contextlib

try:
    from functools import partialmethod
except ImportError:
    # Python 2 fallback: https://gist.github.com/carymrobbins/8940382
    from functools import partial

    class partialmethod(partial):
        def __get__(self, instance, owner):
            if instance is None:
                return self

            return partial(self.func, instance, *(self.args or ()), **(self.keywords or {}))


class CARTOUser(object):

    def __init__(self, user_name=None, org_name=None,
                 api_url=None, api_key=None, check_ssl=True):
        self.user_name = user_name
        self.org_name = org_name
        self.api_url = api_url
        self.api_key = api_key

        if not check_ssl:
            old_request = requests.Session.request
            requests.Session.request = partialmethod(old_request, verify=False)
            warnings.filterwarnings('ignore', 'Unverified HTTPS request')

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
        self.batch_client = BatchSQLClient(self.client)

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

    def batch_check(self,job_id):
        try:
            self.batch_client
        except AttributeError:
            self.initialize()
        return self.batch_client.read(job_id)

    def batch_create(self,query):
        try:
            self.batch_client
        except AttributeError:
            self.initialize()
        return self.batch_client.create(query)

    def batch_cancel(self,job_id):
        try:
            self.batch_client
        except AttributeError:
            self.initialize()
        return self.batch_client.cancel(job_id)

    def get_dataset_manager(self):
        try:
            self.sql_client
        except AttributeError:
            self.initialize()
        return DatasetManager(self.client)


    def get_sync_manager(self):
        try:
            self.sql_client
        except AttributeError:
            self.initialize()
        return SyncTableJobManager(self.client)

    def upload(self,uri,sync_time=None):
        try:
            self.sql_client
        except AttributeError:
            self.initialize()

        dataset_manager = DatasetManager(self.client)

        if sync_time:
            return dataset_manager.create(uri, sync_time)
        else:
            return dataset_manager.create(uri)
