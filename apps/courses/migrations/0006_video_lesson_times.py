# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-10 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_video_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='lesson_times',
            field=models.IntegerField(default=0, verbose_name='学习时长(分钟数）'),
        ),
    ]