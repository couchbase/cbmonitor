from django.db import models
from django.contrib import admin


class Cluster(models.Model):

    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Server(models.Model):

    cluster = models.ForeignKey('Cluster')
    address = models.CharField(max_length=80, primary_key=True)
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


class BucketType(models.Model):

    type = models.CharField(max_length=9)

    def __str__(self):
        return self.type

    class Admin:
        pass


class Bucket(models.Model):

    class Meta:

        unique_together = ["name", "server"]

    server = models.ForeignKey('Server')
    name = models.CharField(max_length=25, default="default")
    type = models.ForeignKey("BucketType")
    port = models.IntegerField(default=11211)
    password = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Metric(models.Model):

    class Meta:

        unique_together = ["name", "cluster", "server", "bucket"]

    cluster = models.ForeignKey("Cluster", null=True, blank=True)
    server = models.ForeignKey("Server", null=True, blank=True)
    bucket = models.ForeignKey("Bucket", null=True, blank=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Admin:
        pass


class Event(models.Model):

    class Meta:

        unique_together = ["name", "cluster", "server", "bucket"]

    cluster = models.ForeignKey("Cluster", null=True, blank=True)
    server = models.ForeignKey("Server", null=True, blank=True)
    bucket = models.ForeignKey("Bucket", null=True, blank=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Admin:
        pass

admin.site.register(Cluster)
admin.site.register(Server)
admin.site.register(Bucket)
admin.site.register(Metric)
admin.site.register(Event)
