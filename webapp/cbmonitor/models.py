from django.db import models
from django.contrib import admin


class Cluster(models.Model):

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Server(models.Model):

    cluster = models.ForeignKey('Cluster')
    address = models.CharField(max_length=80)
    rest_username = models.CharField(max_length=25)
    rest_password = models.CharField(max_length=50)
    ssh_username = models.CharField(max_length=25)
    ssh_password = models.CharField(max_length=50, null=True, blank=True)
    ssh_key = models.CharField(max_length=4096, null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.address

    class Admin:
        pass


admin.site.register(Cluster)
admin.site.register(Server)
