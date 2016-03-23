# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0004_project_test_env2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='test_env',
        ),
    ]
