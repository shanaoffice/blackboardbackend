# Generated by Django 4.2.3 on 2023-09-23 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_customuser_device_id_customuser_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='device_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='employee_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]