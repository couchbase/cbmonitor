import datetime
import glob
import json
import os
import time
from uuid import uuid4
from random import randint, choice

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
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
        response = views.tab(request)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        request = self.factory.get('/charts')
        response = views.tab(request)
        self.assertEqual(response.status_code, 200)

    def test_snapshots(self):
        request = self.factory.get('/snapshots')
        response = views.tab(request)
        self.assertEqual(response.status_code, 200)

    def test_not_existing_page(self):
        request = self.factory.get('/404')
        self.assertRaises(Http404, views.tab, request)


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

    def delete_item(self, item, params):
        """Add new cluster/server/bucket"""
        request = self.factory.post("/delete_" + item, params)
        response = rest_api.dispatcher(request, path="delete_" + item)
        return response


class ApiTest(TestHelper):

    fixtures = ["bucket_type.json", "testdata.json"]

    def setUp(self):
        self.factory = RequestFactory()

    @Verifier.valid_response
    def test_add_cluster(self):
        """Adding new cluster with full set of params"""
        params = {
            "name": uhex(), "rest_username": uhex(), "rest_password": uhex(),
            "description": uhex()
        }
        self.response = self.add_item("cluster", params)

        # Verify persistence
        cluster = models.Cluster.objects.get(name=params["name"])
        self.assertEqual(cluster.description, params["description"])

    @Verifier.valid_response
    def test_add_cluster_wo_description(self):
        """Adding new cluster with missing optional params"""
        params = {
            "name": uhex(), "rest_username": uhex(), "rest_password": uhex()
        }
        self.response = self.add_item("cluster", params)

        # Verify persistence
        cluster = models.Cluster.objects.get(name=params["name"])
        self.assertEqual(cluster.description, "")

    @Verifier.duplicate
    def test_add_cluster_duplicate(self):
        """Adding duplicate cluster"""
        params = {
            "name": uhex(), "rest_username": uhex(), "rest_password": uhex()
        }
        self.add_item("cluster", params)
        self.response = self.add_item("cluster", params)

    @Verifier.missing_parameter
    def test_add_cluster_wo_name(self):
        """Adding new cluster with missing mandatory params"""
        params = {"description": uhex()}
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

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }
        self.response = self.add_item("server", params)

        # Verify persistence
        server = models.Server.objects.get(address=params["address"])
        self.assertEqual(server.cluster.name, cluster)

    @Verifier.bad_parent
    def test_add_server_to_wrong_cluster(self):
        """Adding new server with wrong cluster parameter"""
        params = {
            "cluster": uhex(), "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }

        self.response = self.add_item("server", params)

    @Verifier.valid_response
    def test_add_server_wo_ssh_credentials(self):
        """Adding new server w/o SSH password and key"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(),
            "description": uhex()
        }
        self.response = self.add_item("server", params)

    @Verifier.valid_response
    def test_add_bucket(self):
        """Adding new bucket with full set of params"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster,
            "name": uhex(), "type": choice(("Couchbase", "Memcached")),
            "port": randint(1, 65535), "password": uhex()
        }
        self.response = self.add_item("bucket", params)

        # Verify persistence
        bucket = models.Bucket.objects.get(name=params["name"])
        self.assertEqual(bucket.cluster.name, cluster)

    @Verifier.bad_parameter
    def test_add_bucket_with_wrong_port(self):
        """Adding new bucket with wrong type of port parameter"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster,
            "name": uhex(), "type": choice(("Couchbase", "Memcached")),
            "port": uhex(), "password": uhex()
        }
        self.response = self.add_item("bucket", params)

    @Verifier.bad_parent
    def test_add_bucket_with_wrong_type(self):
        """Adding new bucket with wrong type parameter"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster,
            "name": uhex(), "type": uhex(),
            "port": randint(1, 65535), "password": uhex()
        }
        self.response = self.add_item("bucket", params)

    @Verifier.valid_response
    def test_remove_cluster(self):
        """Removing existing cluster"""
        cluster = self.add_valid_cluster()

        self.response = self.delete_item("cluster", {"name": cluster})

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Cluster.objects.get,
                          name=cluster)

    @Verifier.not_existing
    def test_remove_cluster_not_existing(self):
        """Removing not existing cluster"""
        self.response = self.delete_item("cluster", {"name": uhex()})

    @Verifier.valid_response
    def test_remove_server(self):
        """Removing existing cluster"""
        cluster = self.add_valid_cluster()

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }
        self.add_item("server", params)

        self.response = self.delete_item(
            "server", {"address": params["address"], "cluster": cluster})

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Server.objects.get,
                          address=params["address"])

    @Verifier.valid_response
    def test_remove_bucket(self):
        """Removing existing cluster"""
        cluster = self.add_valid_cluster()

        params = {
            "name": uhex(), "cluster": cluster,
            "type": choice(("Couchbase", "Memcached")),
            "port": randint(1, 65535), "password": uhex()
        }
        self.add_item("bucket", params)

        self.response = self.delete_item("bucket",
                                         {"name": params["name"],
                                          "cluster": cluster})

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Bucket.objects.get,
                          name=params["name"], cluster=cluster)

    @Verifier.valid_json
    def test_get_tree_data(self):
        request = self.factory.get("/get_tree_data")
        self.response = rest_api.dispatcher(request, path="get_tree_data")

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
            params = {"type": "metric",
                      "cluster": "East",
                      "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                      "bucket": "default",
                      "collector": "ns_server"}
            expected = [{"name": "cache_miss", "collector": "ns_server"}]
        else:
            expected = [
                {"name": "cache_miss", "collector": "ns_server"},
                {"name": params["name"], "collector": params["collector"]}
            ]
        request = self.factory.get("/get_metrics_and_events", params)
        self.response = rest_api.dispatcher(request,
                                            path="get_metrics_and_events")

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
        request = self.factory.get("/get_metrics_and_events", params)
        self.response = rest_api.dispatcher(request,
                                            path="get_metrics_and_events")

        # Verify content
        self.assertEquals(sorted(self.response.content),
                          sorted(json.dumps(expected)))

    @Verifier.valid_json
    def test_get_events(self, params=None):
        if not params:
            params = {"type": "event",
                      "cluster": "East",
                      "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                      "bucket": "default"}
            expected = [{"name": "Rebalance start", "collector": "ns_server"}]
        else:
            expected = [
                {"name": "Rebalance start", "collector": "ns_server"},
                {"name": params["name"], "collector": params["collector"]}
            ]
        request = self.factory.get("/get_metrics_and_events", params)
        self.response = rest_api.dispatcher(request,
                                            path="get_metrics_and_events")

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
        request = self.factory.post("/add_metric_or_event", params)
        response = rest_api.dispatcher(request, path="add_metric_or_event")

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
        request = self.factory.post("/add_metric_or_event", params)
        response = rest_api.dispatcher(request, path="add_metric_or_event")

        # Verify persistence
        self.test_get_metrics(params)

        self.response = response

    @Verifier.bad_parameter
    def test_add_metric_with_too_long_unit(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default",
                  "collector": "ns_server",
                  "unit": uhex()}
        request = self.factory.post("/add_metric_or_event", params)
        response = rest_api.dispatcher(request, path="add_metric_or_event")

        # Verify persistence
        self.response = response

    @Verifier.valid_response
    def test_add_metric_no_server(self):
        params = {"type": "metric",
                  "name": uhex(),
                  "cluster": "East",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric_or_event", params)
        response = rest_api.dispatcher(request, path="add_metric_or_event")

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
        request = self.factory.post("/add_metric_or_event", params)
        rest_api.dispatcher(request, path="add_metric_or_event")
        response = rest_api.dispatcher(request, path="add_metric_or_event")

        self.response = response

    @Verifier.valid_response
    def test_add_event(self):
        params = {"type": "event",
                  "name": uhex(),
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric_or_event", params)
        response = rest_api.dispatcher(request, path="add_metric_or_event")

        # Verify persistence
        self.test_get_events(params)

        self.response = response

    @Verifier.missing_parameter
    def test_add_event_no_cluster(self):
        params = {"type": uhex(),
                  "name": "failover",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default",
                  "collector": "ns_server"}
        request = self.factory.post("/add_metric_or_event", params)
        self.response = rest_api.dispatcher(request,
                                            path="add_metric_or_event")

    @Verifier.valid_response
    def test_add_snapshot(self):
        cluster = self.add_valid_cluster()

        ts = datetime.datetime(2000, 1, 1, 0, 0, 0)
        params = {"cluster": cluster, "name": uhex(),
                  "ts_from": ts, "ts_to": ts, "description": uhex()}
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
        request = self.factory.get("/get_snapshots")
        self.response = rest_api.dispatcher(request, path="get_snapshots")

        # Verify content
        expected = json.dumps(["run-1_access-phase_vperf-reb_2.0.0-1976"])
        self.assertEquals(self.response.content, expected)

    @patch('seriesly.core.Database.query', autospec=True)
    @Verifier.valid_json
    def test_plot(self, query_mock):
        query_mock.return_value = {1: [2]}

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "FullReport"}
        request = self.factory.post("/plot", params)
        self.response = rest_api.dispatcher(request, path="plot")

        # Verify content
        expected = [
            "[default] disk_write_queue",
            "[ec2-54-242-160-13.compute-1.amazonaws.com default] cache_miss"
        ]
        titles = [url[0] for url in json.loads(self.response.content)]
        self.assertEquals(titles, expected)
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.png"))

    @patch('seriesly.core.Database.query', autospec=True)
    @Verifier.valid_json
    def test_plot_xdcr(self, query_mock):
        query_mock.return_value = {1: [2]}

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "BaseXdcrReport"}
        request = self.factory.post("/plot", params)
        self.response = rest_api.dispatcher(request, path="plot")
        self.response = rest_api.dispatcher(request, path="plot")

        # Verify content
        expected = ["[default] disk_write_queue"]
        titles = [url[0] for url in json.loads(self.response.content)]
        self.assertEquals(titles, expected)
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.png"))

    @patch('seriesly.core.Database.query', autospec=True)
    def test_pdf(self, query_mock):
        query_mock.return_value = {1: [2]}

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "FullReport"}
        request = self.factory.post("/pdf", params)
        self.response = rest_api.dispatcher(request, path="pdf")

        self.assertEqual("/media/run-1_access-phase_vperf-reb_2.0.0-1976.pdf",
                         self.response.content)
        self.assertTrue(os.path.exists("webapp" + self.response.content))
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.png"))
        map(lambda f: os.remove(f), glob.glob("webapp/media/*.pdf"))

    @patch('seriesly.core.Database.query', autospec=True)
    def test_html(self, query_mock):
        query_mock.return_value = {1: [2]}

        params = {"snapshot": "run-1_access-phase_vperf-reb_2.0.0-1976",
                  "report": "BaseReport"}
        request = self.factory.get("/reports/html", params)
        self.response = views.report(request)

        expected = 'src="/media/run-1_access-phase_vperf-reb_2.0.0-1976Eastdefaultdisk_write_queue.png"'
        self.assertIn(expected, self.response.content)
