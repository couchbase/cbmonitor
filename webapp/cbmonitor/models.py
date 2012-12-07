from django.db import models
from django.contrib import admin


class Cluster(models.Model):

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass

admin.site.register(Cluster)
