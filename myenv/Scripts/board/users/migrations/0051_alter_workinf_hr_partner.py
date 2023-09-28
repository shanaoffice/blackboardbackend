# Generated by Django 4.2.3 on 2023-09-28 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0050_alter_workinf_hr_partner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workinf',
            name='hr_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hr_partner_for', to=settings.AUTH_USER_MODEL),
        ),
    ]