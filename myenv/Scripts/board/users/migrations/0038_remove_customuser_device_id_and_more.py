# Generated by Django 4.2.3 on 2023-09-23 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_alter_customuser_device_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='device_id',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='employee_id',
        ),
    ]