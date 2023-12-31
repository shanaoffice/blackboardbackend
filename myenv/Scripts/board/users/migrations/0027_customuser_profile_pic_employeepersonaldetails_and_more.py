# Generated by Django 4.2.3 on 2023-09-21 12:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_rename_team_id_teamshift_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='profile_pic',
            field=models.CharField(blank=True, default='https://e7.pngegg.com/pngimages/114/356/png-clipart-time-student-recruitment-learning-professional-others-service-vector-icons-thumbnail.png', max_length=200),
        ),
        migrations.CreateModel(
            name='EmployeePersonalDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(blank=True, max_length=20)),
                ('dob', models.DateField(blank=True)),
                ('age', models.PositiveIntegerField(blank=True)),
                ('emg_cont_number', models.CharField(blank=True, max_length=20)),
                ('mother_tongue', models.CharField(blank=True, max_length=100)),
                ('father_name', models.CharField(blank=True, max_length=100)),
                ('mother_name', models.CharField(blank=True, max_length=100)),
                ('employee_p', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeGeneric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievements', models.CharField(blank=True, max_length=100)),
                ('remarks', models.CharField(blank=True, max_length=100)),
                ('contact_number', models.CharField(blank=True, max_length=20)),
                ('employee_s', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('employee_a', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
