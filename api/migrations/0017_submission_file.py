# Generated by Django 3.1 on 2022-12-09 07:09

import api.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20221208_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=api.utils.file_generate_upload_path),
        ),
    ]