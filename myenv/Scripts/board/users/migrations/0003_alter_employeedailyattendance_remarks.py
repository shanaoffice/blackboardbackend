# Generated by Django 4.2.3 on 2023-07-19 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_employeedailyattendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeedailyattendance',
            name='remarks',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
