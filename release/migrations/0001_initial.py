# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('ip', models.GenericIPAddressField()),
                ('env', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('start_cmd', models.CharField(max_length=100)),
                ('stop_cmd', models.CharField(max_length=100)),
                ('target', models.CharField(max_length=100)),
                ('repos', models.CharField(max_length=100)),
                ('test_env', models.GenericIPAddressField()),
                ('test_env2', models.GenericIPAddressField()),
                ('test_env3', models.GenericIPAddressField()),
            ],
        ),
    ]
