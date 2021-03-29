# Generated by Django 3.1.7 on 2021-03-22 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0032_answers_question_quiz'),
    ]

    operations = [
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='class.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='class.student')),
            ],
        ),
    ]