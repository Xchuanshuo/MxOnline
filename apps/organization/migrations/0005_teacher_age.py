# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-11 10:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_teacher_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='age',
            field=models.IntegerField(default=18, max_length=3, verbose_name='年龄'),
        ),
    ]
