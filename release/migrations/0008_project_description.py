# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0007_auto_20160316_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.CharField(max_length=10, default=datetime.datetime(2016, 3, 23, 9, 36, 54, 523956, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
