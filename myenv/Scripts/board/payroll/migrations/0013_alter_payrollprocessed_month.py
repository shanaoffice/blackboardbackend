# Generated by Django 4.2.3 on 2023-09-01 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0012_payrollprocessed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payrollprocessed',
            name='month',
            field=models.CharField(max_length=25),
        ),
    ]