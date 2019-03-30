# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_hostinfo_bk_cloud_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='last_user',
            field=models.CharField(default=b'admin', max_length=50, verbose_name='\u7528\u6237\u540d'),
        ),
    ]
