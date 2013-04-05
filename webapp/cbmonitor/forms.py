from django import forms
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from django.db.utils import IntegrityError

from cbagent.settings import Settings

from cbmonitor import models


class AddClusterForm(forms.ModelForm):

    class Meta:
        model = models.Cluster

    def clean(self):
        cleaned_data = super(AddClusterForm, self).clean()
        cleaned_data["cluster"] = cleaned_data.get("name")
        self.settings = Settings(cleaned_data)
        return cleaned_data


class AddServerForm(forms.ModelForm):

    class Meta:
        model = models.Server


class AddBucketForm(forms.ModelForm):

    class Meta:
        model = models.Bucket


class DeleteClusterForm(forms.ModelForm):

    class Meta:
        model = models.Cluster
        fields = ("name", )


class DeleteServerForm(forms.ModelForm):

    class Meta:
        model = models.Server
        fields = ("address", )


class DeleteBucketForm(forms.ModelForm):

    class Meta:
        model = models.Bucket
        fields = ("cluster", "name")


class GetServersForm(forms.ModelForm):

    class Meta:
        model = models.Server
        fields = ("cluster", )


class GetBucketsForm(forms.ModelForm):

    class Meta:
        model = models.Bucket
        fields = ("cluster", )


class GetMetricsAndEvents(forms.ModelForm):

    bucket = forms.CharField(max_length=32, required=False)

    class Meta:
        model = models.Observable
        fields = ("type", "cluster", "server")

    def clean(self):
        cleaned_data = super(GetMetricsAndEvents, self).clean()

        # Type and Cluster
        cluster = cleaned_data.get("cluster")
        self.params = {
            "type": cleaned_data.get("type"),
            "cluster": cluster
        }

        # Server
        server = cleaned_data["server"]
        if server:
            self.params.update({"server": server})
        else:
            self.params.update({"server__isnull": True})

        # Bucket
        try:
            bucket = models.Bucket.objects.get(name=cleaned_data["bucket"],
                                               cluster=cluster)
            self.params.update({"bucket": bucket})
        except (DoesNotExist, KeyError):
            self.params.update({"bucket__isnull": True})

        return cleaned_data


class AddMetricsAndEvents(forms.ModelForm):

    bucket = forms.CharField(max_length=32, required=False)

    class Meta:
        model = models.Observable
        fields = ("name", "type", "cluster", "server", "collector",
                  "description", "unit")

    def clean(self):
        cleaned_data = super(AddMetricsAndEvents, self).clean()

        try:
            bucket = models.Bucket.objects.get(
                name=cleaned_data["bucket"], cluster=cleaned_data.get("cluster"))
        except (DoesNotExist, KeyError):
            bucket = None
        cleaned_data["bucket"] = bucket

        if cleaned_data["server"] is None:
            try:
                models.Observable.objects.get(name=cleaned_data["name"],
                                              cluster=cleaned_data["cluster"],
                                              server=cleaned_data["server"],
                                              bucket=cleaned_data["bucket"])
                raise IntegrityError("Null server is not unique")
            except DoesNotExist:
                pass

        return cleaned_data


class AddSnapshot(forms.ModelForm):

    class Meta:
        model = models.Snapshot


class GetSnapshots(forms.ModelForm):

    class Meta:
        model = models.Snapshot
        fields = ("cluster", )


class GetCollectors(forms.ModelForm):

    class Meta:
        model = models.Collector
        fields = ("cluster", )
