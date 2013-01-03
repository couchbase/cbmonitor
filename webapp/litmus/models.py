from django.db import models
from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings as DjangoSettings


class Settings(models.Model):
    testcase = models.CharField(max_length=128)
    metric = models.CharField(max_length=128)
    beseline = models.CharField(max_length=128, default=DjangoSettings.LITMUS_BASELINE)
    warning = models.FloatField(validators=[MinValueValidator(-1.0),
                                            MaxValueValidator(1.0)],
                                default=DjangoSettings.LITMUS_WARNING)
    error = models.FloatField(validators=[MinValueValidator(-1.0),
                                          MaxValueValidator(1.0)],
                              default=DjangoSettings.LITMUS_ERROR)

    class Meta:
        unique_together = ("testcase", "metric")


class TestResults(models.Model):
    build = models.CharField(max_length=50)
    timestamp = models.CharField(max_length=20)
    env = models.CharField(max_length=128)
    testcase = models.CharField(max_length=128)
    metric = models.CharField(max_length=128)
    comment = models.CharField(max_length=1024)
    tag = models.CharField(max_length=1024)
    settings = models.ForeignKey(Settings)

    class Meta:
        unique_together = ("testcase", "env", "metric", "build")

    class Admin:
        pass


class Value(models.Model):
    value = models.FloatField(null=True, blank=True)
    test_results = models.ForeignKey(TestResults)


admin.site.register(Settings)
admin.site.register(Value)
admin.site.register(TestResults)
