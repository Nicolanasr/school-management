# Generated by Django 3.1.7 on 2021-03-25 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0037_auto_20210325_1442'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='score_to_pass',
        ),
        migrations.AddField(
            model_name='quiz',
            name='points',
            field=models.IntegerField(default=100),
        ),
    ]