# Generated by Django 3.1.7 on 2021-03-12 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0009_files_file_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='files',
            name='files',
        ),
        migrations.AddField(
            model_name='files',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]