from django.utils import unittest
from django.test.client import RequestFactory

import views


class BasicTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_index(self):
        request = self.factory.get('/')
        response = views.index(request)
        self.assertEqual(response.status_code, 200)
