# Generated by Django 4.2.3 on 2023-09-28 08:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0049_remove_workinf_role_customuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workinf',
            name='hr_partner',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='hr_partner_for', to=settings.AUTH_USER_MODEL),
        ),
    ]