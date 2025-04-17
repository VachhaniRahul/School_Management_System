# Generated by Django 5.1.4 on 2024-12-16 09:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0010_alter_assignmentsubmission_assignment_and_more'),
        ('teacher', '0008_alter_assignment_due_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='class_name',
        ),
        migrations.AddField(
            model_name='student',
            name='class_name',
            field=models.ForeignKey(blank=True, default='1', on_delete=django.db.models.deletion.CASCADE, related_name='students', to='teacher.class'),
            preserve_default=False,
        ),
    ]
