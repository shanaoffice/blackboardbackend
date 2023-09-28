# Generated by Django 4.2.3 on 2023-08-30 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payroll', '0008_alter_salaryhistory_due_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sick_leave_balance', models.PositiveIntegerField(default=0)),
                ('paid_leave_balance', models.PositiveIntegerField(default=0)),
                ('financial_year', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]