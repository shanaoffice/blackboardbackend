# Generated by Django 4.2.3 on 2023-09-25 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0041_alter_customuser_device_id_alter_customuser_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeshift',
            name='shift',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.shift'),
        ),
    ]
