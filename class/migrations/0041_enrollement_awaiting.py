# Generated by Django 3.1.7 on 2021-03-30 14:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0040_submittedassignments_submitted_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollement_awaiting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='class.student')),
            ],
        ),
    ]
