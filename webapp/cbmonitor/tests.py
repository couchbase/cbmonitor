import json
from uuid import uuid4
from random import randint, choice

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ObjectDoesNotExist

import views
import rest_api
import models

uhex = lambda: uuid4().hex


class BasicTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_index(self):
        request = self.factory.get('/')
        response = views.index(request)
        self.assertEqual(response.status_code, 200)


class ApiTest(TestCase):

    fixtures = ["bucket_type.json", "testdata.json"]

    def setUp(self):
        self.factory = RequestFactory()

    def add_item(self, item, params):
        """Add new cluster/server/bucket"""
        request = self.factory.post("/add_" + item, params)
        response = rest_api.dispatcher(request, path="add_" + item)
        return response

    def delete_item(self, item, params):
        """Add new cluster/server/bucket"""
        request = self.factory.post("/delete_" + item, params)
        response = rest_api.dispatcher(request, path="delete_" + item)
        return response

    def verify_valid_response(self, response):
        self.assertEqual(response.content, "Success")
        self.assertEqual(response.status_code, 200)

    def verify_missing_parameter(self, response):
        self.assertTrue("field is required" in response.content)
        self.assertEqual(response.status_code, 400)

    def verify_duplicate(self, response):
        self.assertTrue("already exists" in response.content)
        self.assertEqual(response.status_code, 400)

    def verify_bad_parent(self, response):
        self.assertTrue(
            "does not exist" in response.content or
            "Select a valid choice" in response.content
        )
        self.assertEqual(response.status_code, 400)

    def verify_not_existing(self, response):
        self.assertTrue("matches the given query" in response.content)
        self.assertEqual(response.status_code, 404)

    def verify_bad_parameter(self, response):
        self.assertTrue("Enter a whole number" in response.content)
        self.assertEqual(response.status_code, 400)

    def verify_valid_json(self, response):
        json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_add_cluster(self):
        """Adding new cluster with full set of params"""
        params = {"name": uhex(), "description": uhex()}
        response = self.add_item("cluster", params)

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        cluster = models.Cluster.objects.get(name=params["name"])
        self.assertEqual(cluster.description, params["description"])

    def test_add_cluster_wo_description(self):
        """Adding new cluster with missing optional params"""
        params = {"name": uhex()}
        response = self.add_item("cluster", params)

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        cluster = models.Cluster.objects.get(name=params["name"])
        self.assertEqual(cluster.description, "")

    def test_add_cluster_duplicate(self):
        """Adding duplicate cluster"""
        params = {"name": uhex()}

        # Verify response
        response = self.add_item("cluster", params)
        self.verify_valid_response(response)

        response = self.add_item("cluster", params)
        self.verify_duplicate(response)

    def test_add_cluster_wo_name(self):
        """Adding new cluster with missing mandatory params"""
        params = {"description": uhex()}
        response = self.add_item("cluster", params)

        # Verify response
        self.verify_missing_parameter(response)

    def test_add_cluster_with_empty_name(self):
        """Adding new cluster with empty mandatory params"""
        params = {"name": ""}
        response = self.add_item("cluster", params)

        # Verify response
        self.verify_missing_parameter(response)

    def test_add_server(self):
        """Adding new server with full set of params"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }

        response = self.add_item("server", params)

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        server = models.Server.objects.get(address=params["address"])
        self.assertEqual(server.cluster.name, cluster)

    def test_add_server_to_wrong_cluster(self):
        """Adding new server with wrong cluster parameter"""
        params = {
            "cluster": uhex(), "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }

        response = self.add_item("server", params)

        # Verify response
        self.verify_bad_parent(response)

    def test_add_server_wo_ssh_credentials(self):
        """Adding new server w/o SSH password and key"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(),
            "description": uhex()
        }

        response = self.add_item("server", params)

        # Verify response
        self.verify_missing_parameter(response)

    def test_add_bucket(self):
        """Adding new bucket with full set of params"""

        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        server = uhex()
        params = {
            "cluster": cluster, "address": server,
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex()
        }
        self.add_item("server", params)

        params = {
            "cluster": cluster,
            "name": uhex(), "type": choice(("Couchbase", "Memcached")),
            "port": randint(1, 65535), "password": uhex()
        }
        response = self.add_item("bucket", params)

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        bucket = models.Bucket.objects.get(name=params["name"])
        self.assertEqual(bucket.cluster.name, cluster)

    def test_add_bucket_with_wrong_port(self):
        """Adding new bucket with wrong type of port parameter"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        server = uhex()
        params = {
            "cluster": cluster, "address": server,
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex()
        }
        self.add_item("server", params)

        params = {
            "server": server,
            "name": uhex(), "type": choice(("Couchbase", "Memcached")),
            "port": uhex(), "password": uhex()
        }
        response = self.add_item("bucket", params)

        # Verify response
        self.verify_bad_parameter(response)

    def test_add_bucket_with_wrong_type(self):
        """Adding new bucket with wrong type parameter"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        server = uhex()
        params = {
            "cluster": cluster, "address": server,
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex()
        }
        self.add_item("server", params)

        params = {
            "server": server,
            "name": uhex(), "type": uhex(),
            "port": randint(1, 65535), "password": uhex()
        }
        response = self.add_item("bucket", params)

        # Verify response
        self.verify_bad_parent(response)

    def test_remove_cluster(self):
        """Removing existing cluster"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})

        response = self.delete_item("cluster", {"name": cluster})

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Cluster.objects.get,
                          name=cluster)

    def test_remove_cluster_not_existing(self):
        """Removing not existing cluster"""
        response = self.delete_item("cluster", {"name": uhex()})

        # Verify response
        self.verify_not_existing(response)

    def test_remove_server(self):
        """Removing existing cluster"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})
        params = {
            "cluster": cluster, "address": uhex(),
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }
        self.add_item("server", params)

        response = self.delete_item("server", {"address": params["address"]})

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Server.objects.get,
                          address=params["address"])

    def test_remove_bucket(self):
        """Removing existing cluster"""
        cluster = uhex()
        self.add_item("cluster", {"name": cluster})
        server = uhex()
        params = {
            "cluster": cluster, "address": server,
            "rest_username": uhex(), "rest_password": uhex(),
            "ssh_username": uhex(), "ssh_password": uhex(), "ssh_key": uhex(),
            "description": uhex()
        }
        self.add_item("server", params)

        params = {
            "name": uhex(), "cluster": cluster,
            "type": choice(("Couchbase", "Memcached")),
            "port": randint(1, 65535), "password": uhex()
        }
        self.add_item("bucket", params)

        response = self.delete_item("bucket",
                                    {"name": params["name"],
                                     "cluster": cluster})

        # Verify response
        self.verify_valid_response(response)

        # Verify persistence
        self.assertRaises(ObjectDoesNotExist, models.Bucket.objects.get,
                          name=params["name"], cluster=cluster)

    def test_get_tree_data(self):
        request = self.factory.get("/get_tree_data")
        response = rest_api.dispatcher(request, path="get_tree_data")

        self.verify_valid_json(response)

    def test_get_clusters(self):
        request = self.factory.get("/get_clusters")
        response = rest_api.dispatcher(request, path="get_clusters")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        self.assertEquals(response.content, json.dumps(["East"]))

    def test_get_servers(self):
        params = {"cluster": "East"}
        request = self.factory.get("/get_servers", params)
        response = rest_api.dispatcher(request, path="get_servers")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        expected = json.dumps(["ec2-54-242-160-13.compute-1.amazonaws.com"])
        self.assertEquals(response.content, expected)

    def test_get_servers_with_missing_param(self):
        request = self.factory.get("/get_servers")
        response = rest_api.dispatcher(request, path="get_servers")

        # Verify response
        self.verify_missing_parameter(response)

    def test_get_servers_wrong_param(self):
        params = {"cluster": "West"}
        request = self.factory.get("/get_servers", params)
        response = rest_api.dispatcher(request, path="get_servers")

        # Verify response
        self.verify_bad_parent(response)

    def test_get_buckets(self):
        params = {"cluster": "East"}
        request = self.factory.get("/get_buckets", params)
        response = rest_api.dispatcher(request, path="get_buckets")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        expected = json.dumps(["default"])
        self.assertEquals(response.content, expected)

    def test_get_metrics(self):
        params = {"type": "metric",
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default"}
        request = self.factory.get("/get_metrics_and_events", params)
        response = rest_api.dispatcher(request, path="get_metrics_and_events")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        expected = json.dumps(["cache_miss"])
        self.assertEquals(response.content, expected)

    def test_get_metrics_no_server(self):
        params = {"type": "metric",
                  "cluster": "East",
                  "bucket": "default"}
        request = self.factory.get("/get_metrics_and_events", params)
        response = rest_api.dispatcher(request, path="get_metrics_and_events")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        expected = json.dumps(["disk_queue"])
        self.assertEquals(response.content, expected)

    def test_get_events(self):
        params = {"type": "event",
                  "cluster": "East",
                  "server": "ec2-54-242-160-13.compute-1.amazonaws.com",
                  "bucket": "default"}
        request = self.factory.get("/get_metrics_and_events", params)
        response = rest_api.dispatcher(request, path="get_metrics_and_events")

        # Verify response
        self.verify_valid_json(response)

        # Verify content
        expected = json.dumps(["Rebalance start"])
        self.assertEquals(response.content, expected)
