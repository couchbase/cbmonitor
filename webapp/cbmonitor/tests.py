import glob
import json
import os
import time
from datetime import datetime
from uuid import uuid4
from random import randint, choice

from calendar import timegm
import pytz
from django.test import TestCase, Client
from django.test.client import RequestFactory
from mock import patch

from cbmonitor import views
from cbmonitor import rest_api
from cbmonitor import models

uhex = lambda: uuid4().hex


class Verifier(object):

    @staticmethod
    def valid_response(test):
        def wrapper(self, *args):
            test(self, *args)
            self.assertEqual(self.response.content, "Success")
            self.assertEqual(self.response.status_code, 200)
        return wrapper

    @staticmethod
    def missing_parameter(test):
        def wrapper(self, *args):
            test(self, *args)
            self.assertTrue("field is required" in self.response.content)
            self.assertEqual(self.response.status_code, 400)
        return wrapper

    @staticmethod
    def duplicate(test):
        def wrapper(self, *args):
            test(self, *args)
            self.assertTrue(
                "already exists" in self.response.content or
                "not unique" in self.response.content
            )
            self.assertEqual(self.response.status_code, 400)
        return wrapper

    @staticmethod
    def bad_parent(test):
        def wrapper(self, *args):
            test(self, *args)
            self.assertTrue(
                "does not exist" in self.response.content or
                "Select a valid choice" in self.response.content
            )
            self.assertEqual(self.response.status_code, 400)
        return wrapper

    @staticmethod
    def not_existing(test):
        def wrapper(self, *args):
            test(self, *args)
            self.assertTrue("matches the given query" in self.response.content)
            self.assertEqual(self.response.status_code, 404)
        return wrapper

    @staticmethod
    def bad_parameter(test):
        def wrapper(self, *args):
            test(self, *args)
            err_messages = ("Enter a whole number",
                            "Ensure this value has at most",
                            "Enter a valid date/time")
            self.assertTrue(
                filter(lambda msg: msg in self.response.content, err_messages)
            )
            self.assertEqual(self.response.status_code, 400)
        return wrapper

    @staticmethod
    def valid_json(test):
        def wrapper(self, *args):
            test(self, *args)
            json.loads(self.response.content)
            self.assertEqual(self.response.status_code, 200)
        return wrapper

    @staticmethod
    def empty_array(test):
        def wrapper(self, *args):
            test(self, *args)
            response_body = json.loads(self.response.content)
            self.assertEqual(response_body, [])
            self.assertEqual(self.response.status_code, 200)
        return wrapper


class BasicTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_index(self):
        request = self.factory.get('/')
        response = views.index(request)
        self.assertEqual(response.status_code, 200)


class TestHelper(TestCase):

    def add_item(self, item, params):
        """Add new cluster/server/bucket"""
        request = self.factory.post("/add_" + item, params)
        response = rest_api.dispatcher(request, path="add_" + item)
        return response

    def add_valid_cluster(self):
        cluster = uhex()
        params = {
            "name": cluster, "rest_username": uhex(), "rest_password": uhex(),
            "description": uhex()
        }
        self.add_item("cluster", params)
        return cluster

    def add_valid_server(self):
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster, "address": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }
        return self.add_item("server", params)

    def add_valid_bucket(self):
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster,
            "name": uhex(), "type": choice(("Couchbase", "Memcached")),
            "port": randint(1, 65535), "password": uhex(),
            "description": uhex()
        }
        return self.add_item("bucket", params)


class ApiTest(TestHelper):

    fixtures = ["bucket_type.json", "testdata.json"]

    def setUp(self):
        self.factory = RequestFactory()

    @Verifier.valid_response
    def test_add_cluster(self):
        """Adding new cluster with full set of params"""
        params = {"name": uhex()}
        self.response = self.add_item("cluster", params)

        # Verify persistence
        cluster = models.Cluster.objects.get(name=params["name"])
        self.assertEqual(cluster.name, params["name"])

    @Verifier.duplicate
    def test_add_cluster_duplicate(self):
        """Adding duplicate cluster"""
        params = {"name": uhex()}
        self.add_item("cluster", params)
        self.response = self.add_item("cluster", params)

    @Verifier.missing_parameter
    def test_add_cluster_wo_name(self):
        """Adding new cluster with missing mandatory params"""
        params = {}
        self.response = self.add_item("cluster", params)

    @Verifier.missing_parameter
    def test_add_cluster_with_empty_name(self):
        """Adding new cluster with empty mandatory params"""
        params = {"name": ""}
        self.response = self.add_item("cluster", params)

    @Verifier.valid_response
    def test_add_server(self):
        """Adding new server with full set of params"""
        cluster = self.add_valid_cluster()

        params = {"cluster": cluster, "address": uhex()}
        self.response = self.add_item("server", params)

        # Verify persistence
        server = models.Server.objects.get(address=params["address"])
        self.assertEqual(server.cluster.name, cluster)

    @Verifier.bad_parent
    def test_add_server_to_wrong_cluster(self):
        """Adding new server with wrong cluster parameter"""
        params = {"cluster": uhex(), "address": uhex()}

        self.response = self.add_item("server", params)

    @Verifier.valid_response
    def test_add_server_with_rest_credentials(self):
        """Adding new server with redundant params"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex()
        }
        self.response = self.add_item("server", params)

    @Verifier.valid_response
    def test_add_bucket(self):
        """Adding new bucket with full set of params"""
        cluster = self.add_valid_cluster()

        params = {"cluster": cluster, "name": uhex()}
        self.response = self.add_item("bucket", params)

        # Verify persistence
        bucket = models.Bucket.objects.get(name=params["name"])
        self.assertEqual(bucket.cluster.name, cluster)

    @Verifier.valid_response
    def test_add_bucket_with_port(self):
        """Adding new bucket with redundant params"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster, "name": uhex(),
            "type": choice(("Couchbase", "Memcached"))
        }
        self.response = self.add_item("bucket", params)

    @Verifier.valid_json
    def test_get_clusters(self):
        request = self.factory.get("/get_clusters")
        self.response = rest_api.dispatcher(request, path="get_clusters")

        # Verify content
        self.assertEquals(self.response.content, json.dumps(["East"]))

    @Verifier.valid_json
    def test_get_servers(self):
        params = {"cluster": "East"}
        request = self.factory.get("/get_servers", params)
        self.response = rest_api.dispatcher(request, path="get_servers")

        # Verify content
        expected = json.dumps(["ec2-54-242-160-13.compute-1.amazonaws.com"])
        self.assertEquals(self.response.content, expected)

    @Verifier.empty_array
    def test_get_servers_with_missing_param(self):
        request = self.factory.get("/get_servers")
        self.response = rest_api.dispatcher(request, path="get_servers")

    @Verifier.empty_array
    def test_get_servers_wrong_param(self):
        params = {"cluster": "West"}
        request = self.factory.get("/get_servers", params)
        self.response = rest_api.dispatcher(request, path="get_servers")

    @Verifier.valid_json
    def test_get_buckets(self):
        params = {"cluster": "East"}
        request = self.factory.get("/get_buckets", params)
        self.response = rest_api.dispatcher(request, path="get_buckets")

        # Verify content
        expected = json.dumps(["default"])
        self.assertEquals(self.response.content, expected)

    @Verifier.valid_json
    def test_get_metrics(self, params=None):
        if not params:
            params = {"cluster": "East",
                      "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                      "bucket": "default",
                      "collector": "ns_server"}
            expected = [{"name": "cache_miss", "collector": "ns_server"}]
        else:
            expected = [
                {"name": "cache_miss", "collector": "ns_server"},
                {"name": params["name"], "collector": params["collector"]}
            ]
        request = self.factory.get("/get_metrics", params)
        self.response = rest_api.dispatcher(request,
                                            path="get_metrics")

        # Verify content
        self.assertEquals(sorted(self.response.content),
                          sorted(json.dumps(expected)))

    @Verifier.valid_json
    def test_get_metrics_no_server(self, params=None):
        if not params:
            params = {"type": "metric",
                      "cluster": "East",
                      "bucket": "default"}
            expected = [{"name": "disk_write_queue", "collector": "ns_server"}]
        else:
            expected = [
                {"name": "disk_write_queue", "collector": "ns_server"},
                {"name": params["name"], "collector": params["collector"]}
            ]
        request = self.factory.get("/get_metrics", params)
        self.response = rest_api.dispatcher(request,
                                            path="get_metrics")

        # Verify content
        self.assertEquals(sorted(self.response.content),
                          sorted(json.dumps(expected)))

    @Verifier.valid_response
    def test_add_metric(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric", params)
        response = rest_api.dispatcher(request, path="add_metric")

        # Verify persistence
        self.test_get_metrics(params)

        self.response = response

    @Verifier.valid_response
    def test_add_metric_with_description(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default",
                  "collector": "ns_server",
                  "description": "new metric"}
        request = self.factory.post("/add_metric", params)
        response = rest_api.dispatcher(request, path="add_metric")

        # Verify persistence
        self.test_get_metrics(params)

        self.response = response

    @Verifier.valid_response
    def test_add_metric_no_server(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric", params)
        response = rest_api.dispatcher(request, path="add_metric")

        # Verify persistence
        self.test_get_metrics_no_server(params)

        self.response = response

    @Verifier.duplicate
    def test_add_metric_duplicate_empty_server(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric", params)
        rest_api.dispatcher(request, path="add_metric")
        response = rest_api.dispatcher(request, path="add_metric")

        self.response = response

    @Verifier.duplicate
    def test_add_metric_duplicate_empty_bucket(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric", params)
        rest_api.dispatcher(request, path="add_metric")
        response = rest_api.dispatcher(request, path="add_metric")

        self.response = response

    @Verifier.valid_response
    def test_add_snapshot(self):
        cluster = self.add_valid_cluster()

        ts = datetime(2000, 1, 1, 0, 0, 0)
        params = {"cluster": cluster, "name": uhex(),
                  "ts_from": ts, "ts_to": ts}
        self.response = self.add_item("snapshot", params)

        # Verify persistence
        snapshot = models.Snapshot.objects.get(name=params["name"])
        self.assertEqual(snapshot.cluster.name, cluster)

    @Verifier.valid_response
    def test_add_cbagent_snapshot(self):
        cluster = self.add_valid_cluster()

        ts_old = datetime.fromtimestamp(time.time(), tz=pytz.utc)
        ts_new = datetime.utcnow()
        self.assertAlmostEqual(timegm(ts_old.timetuple()),
                               timegm(ts_new.timetuple()), delta=10)

        params = {"cluster": cluster, "name": uhex(),
                  "ts_from": datetime.utcnow(), "ts_to": datetime.utcnow()}
        self.response = self.add_item("snapshot", params)

        # Verify persistence
        snapshot = models.Snapshot.objects.get(name=params["name"])
        self.assertEqual(snapshot.cluster.name, cluster)

    @Verifier.bad_parameter
    def test_add_snapshot_with_wrong_ts_type(self):
        cluster = self.add_valid_cluster()

        ts = time.time()
        params = {"cluster": cluster, "name": uhex(),
                  "ts_from": ts, "ts_to": ts, "description": uhex()}
        self.response = self.add_item("snapshot", params)

    @Verifier.valid_json
    def test_get_snapshots(self):
        params = {"cluster": "East"}
        request = self.factory.get("/get_snapshots", params)
        self.response = rest_api.dispatcher(request, path="get_snapshots")

        # Verify content
        expected = json.dumps(["all_data",
                               "run-1_access-phase_vperf-reb_2.0.0-1976"])
        self.assertEquals(self.response.content, expected)

    @patch('seriesly.core.Database.query', autospec=True)
    @patch('seriesly.core.Seriesly.list_dbs', autospec=True)
    def test_xdcr_html_report(self, list_dbs_mock, query_mock):
        query_mock.return_value = {1: [2]}
        list_dbs_mock.return_value = ['ns_serverEastdefault']

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "BaseXdcrReport"}
        Client().get("/reports/html/", params)
        response = Client().get("/reports/html/", params)

        # Verify content
        expected = 'src="/media/run-1_access-phase_vperf-reb_2.0.0-1976Eastdefaultdisk_write_queue.png"'
        self.assertIn(expected, response.content)
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.png"))

    @patch('seriesly.core.Database.query', autospec=True)
    @patch('seriesly.core.Seriesly.list_dbs', autospec=True)
    def test_base_html_report(self, list_dbs_mock, query_mock):
        query_mock.return_value = {1: [2]}
        list_dbs_mock.return_value = ['ns_serverEastdefault']

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "BaseReport"}
        request = self.factory.get("/reports/html/", params)
        self.response = views.html_report(request)

        expected = 'src="/media/run-1_access-phase_vperf-reb_2.0.0-1976Eastdefaultdisk_write_queue.png"'
        self.assertIn(expected, self.response.content)
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.png"))
