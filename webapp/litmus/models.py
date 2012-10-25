from django.db import models

class TestResults(models.Model):
    build = models.CharField(max_length=50)
    timestamp = models.CharField(max_length=20)
    metric = models.CharField(max_length=128)
    value = models.FloatField()
