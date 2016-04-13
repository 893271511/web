# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0009_auto_20160323_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='production_env',
            field=models.ManyToManyField(related_name='production_ip', to='release.Host'),
        ),
        migrations.AddField(
            model_name='project',
            name='proxys',
            field=models.ManyToManyField(related_name='proxy_ip', to='release.Host'),
        ),
        migrations.AddField(
            model_name='project',
            name='port',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='repos',
            field=models.URLField(unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_cmd',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='stop_cmd',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='test_env',
            field=models.ManyToManyField(to='release.Host', related_name='test_ip'),
        ),
    ]
