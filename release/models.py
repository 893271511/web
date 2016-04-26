from django.db import models
from datetime import *


# Create your models here.


class Host(models.Model):
    ip = models.GenericIPAddressField()
    env = models.CharField(max_length=10)

    def __str__(self):
        return self.ip

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

    def __str__(self):
        return self.name

