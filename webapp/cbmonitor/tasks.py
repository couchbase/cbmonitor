from datetime import timedelta
from threading import Thread
from time import sleep

import djcelery
from celery import platforms
from celery.signals import worker_process_init
from celery.task import PeriodicTask
from celery.utils.log import get_task_logger

from cbagent.collectors import NSServer, Atop, ActiveTasks
from cbagent.settings import Settings
from cbmonitor import models


djcelery.models.PeriodicTask.objects.update(last_run_at=None)

logger = get_task_logger(__name__)


class Collector(Thread):

    def __init__(self, db_object):
        super(Collector, self).__init__()
        self.db_object = db_object
        self._stopped = False

    def __repr__(self):
        return "{0}: {1}".format(self.db_object.cluster, self.db_object.name)

    def _get_class(self):
        return {
            "ns_server": NSServer,
            "atop": Atop,
            "Active tasks": ActiveTasks,
        }[str(self.db_object)]

    def _get_settings(self):
        return Settings({
            "cluster": self.db_object.cluster.name,
            "master_node": self.db_object.cluster.master_node,
            "rest_username": self.db_object.cluster.rest_username,
            "rest_password": self.db_object.cluster.rest_password,
        })

    def run(self):
        cls = self._get_class()
        settings = self._get_settings()
        collector = cls(settings)
        collector.update_metadata()
        while not self._stopped:
            collector.collect()
            sleep(self.db_object.interval)

    def stop(self):
        self._stopped = True


class CollectorManager(PeriodicTask):

    run_every = timedelta(seconds=5)

    running_collectors = {}

    def __init__(self):
        worker_process_init.connect(self.handle_signals)

    @staticmethod
    def _get_hash(db_object):
        return hash((db_object.name, db_object.cluster.name))

    def _start_collector(self, db_object):
        hsh = self._get_hash(db_object)
        if hsh not in self.running_collectors:
            logger.info("Starting collector: {0}".format(db_object.name))
            self.running_collectors[hsh] = Collector(db_object)
            self.running_collectors[hsh].start()

    def _stop_collector(self, db_object):
        hsh = self._get_hash(db_object)
        if hsh in self.running_collectors:
            logger.info("Stopping collector: {0}".format(db_object.name))
            self.running_collectors[hsh].stop()
            self.running_collectors.pop(hsh)

    @classmethod
    def shutdown(cls, signum, frame):
        for collector in cls.running_collectors.itervalues():
            collector.stop()
            collector.join()

    @staticmethod
    def handle_signals(**kwargs):
        platforms.signals["TERM"] = CollectorManager.shutdown
        platforms.signals["INT"] = CollectorManager.shutdown

    def run(self, **kwargs):
        logger.info("Running with: {0}".format(self.running_collectors.values()))
        for db_object in models.Collector.objects.all():
            if db_object.enabled:
                self._start_collector(db_object)
            else:
                self._stop_collector(db_object)
