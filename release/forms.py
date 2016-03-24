from django import forms
from django.forms import ModelForm
from release.models import *


class ReleaseForm(forms.Form):
    PROJECT_CHOICES = Project.objects.values_list('name', 'name')
    env = forms.CharField(label=(u"环境"),initial="test",widget=forms.TextInput(attrs={'type': 'hidden'}))
    project = forms.ChoiceField(choices=PROJECT_CHOICES, label='项目')
    version = forms.IntegerField(label=(u"版本号"))



class ReleaseForm2(ModelForm):
    class Meta:
        model = Project
        fields = ['name','test_env']
