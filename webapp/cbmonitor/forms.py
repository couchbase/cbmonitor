from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from cbmonitor import models


class AddClusterForm(forms.ModelForm):
    class Meta:
        model = models.Cluster

    def clean(self):
        cleaned_data = super(AddClusterForm, self).clean()
        cleaned_data["cluster"] = cleaned_data.get("name")
        return cleaned_data


class AddServerForm(forms.ModelForm):
    class Meta:
        model = models.Server


class AddBucketForm(forms.ModelForm):
    class Meta:
        model = models.Bucket


class AddIndexForm(forms.ModelForm):
    class Meta:
        model = models.Index


class GetServersForm(forms.ModelForm):
    class Meta:
        model = models.Server
        fields = ("cluster",)


class GetBucketsForm(forms.ModelForm):
    class Meta:
        model = models.Bucket
        fields = ("cluster",)


class GetIndexForm(forms.ModelForm):
    class Meta:
        model = models.Index
        fields = ("cluster",)


class GetMetrics(forms.ModelForm):
    bucket = forms.CharField(max_length=32, required=False)
    index = forms.CharField(max_length=32, required=False)
    server = forms.CharField(max_length=80, required=False)

    class Meta:
        model = models.Observable
        fields = ("cluster",)

    def clean(self):
        cleaned_data = super(GetMetrics, self).clean()

        # Type and Cluster
        cluster = cleaned_data.get("cluster")
        self.params = {"cluster": cluster}

        # Server
        try:
            server = models.Server.objects.get(
                address=cleaned_data["server"], cluster=cluster)
            self.params.update({"server": server})
        except (ObjectDoesNotExist, KeyError):
            self.params.update({"server__isnull": True})

        # Bucket
        try:
            bucket = models.Bucket.objects.get(
                name=cleaned_data["bucket"], cluster=cluster)
            self.params.update({"bucket": bucket})
        except (ObjectDoesNotExist, KeyError):
            self.params.update({"bucket__isnull": True})

        # Index
        try:
            index = models.Index.objects.get(
                name=cleaned_data["index"], cluster=cluster)
            self.params.update({"index": index})
        except (ObjectDoesNotExist, KeyError):
            self.params.update({"index__isnull": True})

        return cleaned_data


class AddMetric(forms.ModelForm):
    bucket = forms.CharField(max_length=32, required=False)
    index = forms.CharField(max_length=32, required=False)
    server = forms.CharField(max_length=80, required=False)

    class Meta:
        model = models.Observable
        fields = ("name", "cluster", "collector")

    def clean(self):
        cleaned_data = super(AddMetric, self).clean()

        try:
            bucket = models.Bucket.objects.get(
                name=cleaned_data["bucket"],
                cluster=cleaned_data.get("cluster"))
        except (ObjectDoesNotExist, KeyError):
            bucket = None
        cleaned_data["bucket"] = bucket

        try:
            index = models.Index.objects.get(
                name=cleaned_data["index"],
                cluster=cleaned_data.get("cluster"))
        except (ObjectDoesNotExist, KeyError):
            index = None
        cleaned_data["index"] = index

        try:
            server = models.Server.objects.get(
                address=cleaned_data["server"],
                cluster=cleaned_data.get("cluster"))
        except (ObjectDoesNotExist, KeyError):
            server = None
        cleaned_data["server"] = server

        if cleaned_data["server"] is None or cleaned_data["bucket"] is None \
                or cleaned_data["index"] is None:
            try:
                models.Observable.objects.get(name=cleaned_data["name"],
                                              cluster=cleaned_data["cluster"],
                                              server=cleaned_data["server"],
                                              bucket=cleaned_data["bucket"],
                                              index=cleaned_data["index"])
                raise IntegrityError("Observable is not unique")
            except (ObjectDoesNotExist, KeyError):
                pass

        return cleaned_data


class AddSnapshot(forms.ModelForm):
    class Meta:
        model = models.Snapshot
