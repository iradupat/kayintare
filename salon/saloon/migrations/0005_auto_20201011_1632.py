# Generated by Django 3.0.7 on 2020-10-11 14:32

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('saloon', '0004_auto_20201011_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(default=datetime.datetime(2020, 10, 11, 14, 32, 39, 46834, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='message',
            field=models.TextField(max_length=2200),
        ),
    ]
