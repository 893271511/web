from django import forms
from release.models import *


class ReleaseForm(forms.Form):
    PROJECT_CHOICES = Project.objects.values_list('name','name')
    project = forms.ChoiceField(choices=PROJECT_CHOICES, label='项目')
    version = forms.IntegerField(label=(u"版本号"))
