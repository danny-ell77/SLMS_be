# Generated by Django 3.1 on 2022-07-26 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20220726_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='status',
            field=models.CharField(choices=[('PENDING', 'pending'), ('COMPLETED', 'completed')], default='pending', max_length=15),
        ),
    ]
