import os
import signal
import socket
import subprocess
import sys
import time
import unittest

from django.core.management import call_command
from cbmock.helpers import MockHelper

from cbagent.settings import DefaultSettings
from cbagent.collectors import NSServer


class DjangoHelper(object):

    def __init__(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        sys.path.append("webapp")

    def syncdb(self):
        call_command("syncdb", interactive=False)

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
