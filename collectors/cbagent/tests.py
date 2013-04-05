import os
import signal
import socket
import subprocess
import sys
import time
import unittest
from multiprocessing import Process

import requests
from django.core.management import call_command
from cbmock import cbmock

from cbagent.settings import DefaultSettings
from cbagent.collectors import NSServer


class MockHelper(object):

    def __init__(self):
        self.mock = Process(target=cbmock.main, kwargs={"num_nodes": 1})
        self.mock.start()

    def __del__(self):
        self.mock.terminate()

    def train_seriesly(self):
        dbs = ["ns_serverEastdefaultec2-54-242-160-13compute-1amazonawscom",
               "ns_serverEastdefault"]
        for db in dbs:
            params = {
                "path": "/{0}/_query".format(db), "method": "GET",
                "response_code": "200", "response_body": "{}",
            }
            requests.post(url="http://127.0.0.1:8080/", params=params)

    def _submit_sample(self, path, sample):
        base_path = "collectors/cbagent/fixtures/"
        params = {"method": "GET", "response_code": 200, "path": path}
        with open(base_path + sample) as fh:
            requests.post(url="http://127.0.0.1:8080/", params=params,
                          files={"response_body": fh})

    def train_couchbase(self):
        paths = [
            "/pools/default",
            "/pools/default/buckets",
            "/pools/default/buckets/default/nodes",
            "/pools/default/buckets/default/stats",
            "/pools/default/buckets/default/statsDirectory",
            "/pools/default/buckets/default/nodes/127.0.0.1%3A8091/stats"
        ]
        samples = [
            "pools_default.json",
            "pools_default_buckets.json",
            "pools_default_buckets_default_nodes.json",
            "pools_default_buckets_default_stats.json",
            "pools_default_buckets_default_statsDirectory.json",
            "pools_default_buckets_default_nodes_127.0.0.1_stats.json"
        ]
        test_data = dict(zip(paths, samples))
        for path, sample in test_data.iteritems():
            self._submit_sample(path, sample)


class DjangoHelper(object):

    def __init__(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        sys.path.append("webapp")

    def syncdb(self):
        call_command("syncdb", interactive=False)
        call_command("migrate")

    def runserver(self):
        self.server = subprocess.Popen("./bin/webapp runserver --nothreading",
                                       shell=True, preexec_fn=os.setsid)
        s = socket.socket()
        while True:
            try:
                s.connect(("127.0.0.1", 8000))
                break
            except socket.error:
                time.sleep(0.1)

    def __del__(self):
        os.killpg(self.server.pid, signal.SIGTERM)


class CollectorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock = MockHelper()
        cls.mock.train_seriesly()
        cls.mock.train_couchbase()

        cls.django = DjangoHelper()
        cls.django.syncdb()
        cls.django.runserver()

    @classmethod
    def tearDownClass(cls):
        del cls.mock
        del cls.django

    def test_ns_collector_metadata_update(self):
        settings = DefaultSettings()
        ns_collector = NSServer(settings)
        ns_collector.update_metadata()
