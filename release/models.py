from django.db import models
from datetime import *
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import *
from django.utils import timezone

class Host(models.Model):
    ip = models.GenericIPAddressField()
    env = models.CharField(max_length=10)

    def __str__(self):
        return self.ip


class ProjectGroup(models.Model):
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100,null=False,unique=True)
    start_cmd = models.CharField(max_length=100,null=False,unique=True)
    stop_cmd = models.CharField(max_length=100,null=False,unique=True)
    target = models.CharField(max_length=100)
    repos = models.URLField(max_length=200,null=False,unique=True)
    test_env = models.ManyToManyField(Host, related_name='test_ip')
    production_env = models.ManyToManyField(Host, related_name='production_ip')
    staging_env = models.ManyToManyField(Host, related_name='staging_ip')
    port = models.PositiveIntegerField(null=False)
    proxys = models.ManyToManyField(Host, related_name='proxy_ip')
    description = models.CharField(max_length=10)
    group = models.ManyToManyField(ProjectGroup, related_name='group_name')
    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ("release_test_project", "Can release test project"),
            ("release_staging_project", "Can release staging project"),
            ("release_production_project", "Can release production project"),
        )

#
# class ReleaseHistory(models.Model):
#     release_time = models.DateTimeField(auto_now_add=True)
#     release_project = models.CharField(max_length=100,null=False,unique=False)
#     release_user = models.CharField(max_length=100,null=False,unique=False)
#     release_hosts = models.CharField(max_length=100,null=False,unique=False)
#     release_ver = models.CharField(max_length=100,null=False,unique=False)
#     release_status = models.CharField(max_length=50,null=False,unique=False)
#     release_env = models.CharField(max_length=20,null=False,unique=False)
#     def __str__(self):
#         return self.release_project
#


