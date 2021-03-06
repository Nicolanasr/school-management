# Generated by Django 3.1.7 on 2021-03-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0028_submittedassignments_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedassignments',
            name='status',
            field=models.CharField(choices=[('awaiting submission', 'awaiting submission'), ('submitted', 'submitted'), ('graded', 'graded'), ('missed', 'missed')], default=('awaiting submission', 'awaiting submission'), max_length=100),
        ),
        migrations.AlterField(
            model_name='submittedassignments',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to='assignments_files/'),
        ),
    ]
