from django.db import models
from datetime import *
from django.contrib.auth.models import AbstractUser


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


# class UserGroup(models.Model):
#     name = models.CharField(max_length=80, unique=True)
#     comment = models.CharField(max_length=160, blank=True, null=True)
#
#     def __unicode__(self):
#         return self.name

# class User(AbstractUser):
#     # USER_ROLE_CHOICES = (
#     #     ('SU', 'SuperUser'),
#     #     ('GA', 'GroupAdmin'),
#     #     ('CU', 'CommonUser'),
#     # )
#     name = models.CharField(max_length=80)
#     # uuid = models.CharField(max_length=100)
#     # role = models.CharField(max_length=2, choices=USER_ROLE_CHOICES, default='CU')
#     # group = models.ManyToManyField(UserGroup)
#     # ssh_key_pwd = models.CharField(max_length=200)
#     # # is_active = models.BooleanField(default=True)
#     # # last_login = models.DateTimeField(null=True)
#     # # date_joined = models.DateTimeField(null=True)
#     #
#     # def __unicode__(self):
#     #     return self.username
#     #
