# Generated by Django 4.2.3 on 2023-07-20 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_employeedailyattendance_attendance_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeedailyattendance',
            name='check_in_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employeedailyattendance',
            name='check_out_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
