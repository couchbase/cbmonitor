import unittest
from multiprocessing import Process

from cbmock import cbmock


class MockHelper(object):

    def __init__(self):
        self.mock = Process(target=cbmock.main, kwargs={"num_nodes": 1})
        self.mock.start()

    def __del__(self):
        self.mock.terminate()


class CollectorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock = MockHelper()

    @classmethod
    def tearDownClass(cls):
        del cls.mock
