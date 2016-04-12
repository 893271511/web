from django.db import models
from datetime import *


# Create your models here.


class Host(models.Model):
    ip = models.GenericIPAddressField()
    env = models.CharField(max_length=10)

    def __str__(self):
        return self.ip

class Project(models.Model):
    name = models.CharField(max_length=100)
    start_cmd = models.CharField(max_length=100)
    stop_cmd = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    repos = models.URLField(max_length=100)
    test_env = models.ManyToManyField(Host, related_name='test_ip')
    production_env = models.ManyToManyField(Host, related_name='production_ip')
    port = models.PositiveIntegerField(null=True)
    proxys = models.ManyToManyField(Host, related_name='proxy_ip')
    description = models.CharField(max_length=10)

    def __str__(self):
        return self.name

