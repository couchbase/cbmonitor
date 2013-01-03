from django.forms import ModelForm, ValidationError

import models


class AddClusterForm(ModelForm):

    class Meta:
        model = models.Cluster


class AddServerForm(ModelForm):

    class Meta:
        model = models.Server

    def clean(self):
        cleaned_data = super(AddServerForm, self).clean()
        if not cleaned_data["ssh_password"] and not cleaned_data["ssh_key"]:
            raise ValidationError("This field is required.")
        else:
            return cleaned_data


class AddBucketForm(ModelForm):

    class Meta:
        model = models.Bucket


class DeleteClusterForm(ModelForm):

    class Meta:
        model = models.Cluster
        fields = ("name", )


class DeleteServerForm(ModelForm):

    class Meta:
        model = models.Server
        fields = ("address", )


class DeleteBucketForm(ModelForm):

    class Meta:
        model = models.Bucket
        fields = ("cluster", "name")


class GetServersForm(ModelForm):

    class Meta:
        model = models.Server
        fields = ("cluster", )


class GetBucketsForm(ModelForm):

    class Meta:
        model = models.Bucket
        fields = ("cluster", )
