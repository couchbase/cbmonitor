from django.db import models
from django.contrib import admin


class TestResults(models.Model):
    build = models.CharField(max_length=50)
    timestamp = models.CharField(max_length=20)
    metric = models.CharField(max_length=128)
    value = models.FloatField()

    class Admin:
        pass

admin.site.register(TestResults)
