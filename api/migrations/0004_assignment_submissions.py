# Generated by Django 3.1 on 2022-02-08 21:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20220131_0353'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('course', models.CharField(max_length=50)),
                ('course_code', models.CharField(max_length=10)),
                ('duration', models.DateTimeField()),
                ('status', models.CharField(max_length=15)),
                ('marks', models.IntegerField()),
                ('_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='api.userclass')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('title', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=15)),
                ('score', models.FloatField()),
                ('is_draft', models.BooleanField(default=False)),
                ('is_submitted', models.BooleanField(default=False)),
                ('_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='api.userclass')),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='api.assignment')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_date', '-modified_date'],
                'abstract': False,
            },
        ),
    ]
