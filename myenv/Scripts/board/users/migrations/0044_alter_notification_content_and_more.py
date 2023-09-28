# Generated by Django 4.2.3 on 2023-09-26 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_rename_attendance_employeeshift_attendance_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='modal_opened',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='read',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='notification',
            name='to',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]