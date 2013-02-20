from django.db import models
from django.contrib import admin


class Cluster(models.Model):

    name = models.CharField(max_length=64, primary_key=True, blank=False)
    master_node = models.CharField(max_length=128, null=True, blank=True)
    rest_username = models.CharField(max_length=32, blank=False)
    rest_password = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Server(models.Model):

    cluster = models.ForeignKey('Cluster')
    address = models.CharField(max_length=80, primary_key=True, blank=False)
    ssh_username = models.CharField(max_length=32, blank=True)
    ssh_password = models.CharField(max_length=64, blank=True)
    ssh_key = models.CharField(max_length=4096, blank=True)
    description = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return self.address

    class Admin:
        pass


class BucketType(models.Model):

    type = models.CharField(max_length=9, primary_key=True)

    def __str__(self):
        return self.type

    class Admin:
        pass


class Bucket(models.Model):

    class Meta:
        unique_together = ["name", "cluster"]

    name = models.CharField(max_length=32, default="default")
    cluster = models.ForeignKey("Cluster")
    type = models.ForeignKey("BucketType")
    port = models.IntegerField(default=11211, null=True, blank=True)
    password = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass


class ObservableType(models.Model):

    type = models.CharField(max_length=6, primary_key=True)

    def __str__(self):
        return self.type

    class Admin:
        pass


class Observable(models.Model):

    class Meta:
        unique_together = ["name", "cluster", "server", "bucket"]

    name = models.CharField(max_length=64)
    type = models.ForeignKey(ObservableType)
    unit = models.CharField(max_length=16, null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    cluster = models.ForeignKey("Cluster")
    server = models.ForeignKey("Server", null=True, blank=True)
    bucket = models.ForeignKey("Bucket", null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass

admin.site.register(Cluster)
admin.site.register(Server)
admin.site.register(Bucket)
admin.site.register(Observable)
