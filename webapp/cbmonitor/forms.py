from django import forms
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist

import models


class AddClusterForm(forms.ModelForm):

    class Meta:
        model = models.Cluster


class AddServerForm(forms.ModelForm):

    class Meta:
        model = models.Server

    def clean(self):
        cleaned_data = super(AddServerForm, self).clean()
        if not cleaned_data["ssh_password"] and not cleaned_data["ssh_key"]:
            raise forms.ValidationError("This field is required.")
        else:
            return cleaned_data


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

    TYPES = (
        ("metric", "metric"),
        ("event", "event")
    )

    type = forms.ChoiceField(choices=TYPES)
    bucket = forms.CharField(max_length=32, required=False)

    class Meta:
        model = models.Metric
        fields = ("cluster", "server")

    def clean(self):
        cleaned_data = super(GetMetricsAndEvents, self).clean()

        # Cluster
        cluster = cleaned_data.get("cluster")
        self.params = {"cluster": cluster}

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
