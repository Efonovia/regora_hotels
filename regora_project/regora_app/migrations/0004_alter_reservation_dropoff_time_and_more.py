# Generated by Django 4.2 on 2023-05-17 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regora_app', '0003_alter_reservation_pickup_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='dropoff_time',
            field=models.TimeField(blank=True, default='nothing', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='pickup_time',
            field=models.TimeField(blank=True, default='None', max_length=20, null=True),
        ),
    ]
