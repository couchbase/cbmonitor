from django.db import models
from django.contrib import admin


class TestResults(models.Model):
    build = models.CharField(max_length=50)
    timestamp = models.CharField(max_length=20)
    env = models.CharField(max_length=128)
    testcase = models.CharField(max_length=128)
    metric = models.CharField(max_length=128)
    value = models.FloatField(null=True, blank=True)
    comment = models.CharField(max_length=1024)

    class Admin:
        pass

admin.site.register(TestResults)
