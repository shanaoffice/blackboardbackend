# Generated by Django 4.2.3 on 2023-09-23 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_customuser_device_id_customuser_employee_id'),
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
