# Generated by Django 3.0.7 on 2020-10-13 07:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('saloon', '0006_auto_20201013_0929'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Payments',
            new_name='Payment',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(default=datetime.datetime(2020, 10, 13, 7, 50, 52, 101324, tzinfo=utc)),
        ),
    ]
