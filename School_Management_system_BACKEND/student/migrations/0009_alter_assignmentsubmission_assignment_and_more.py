# Generated by Django 5.1.4 on 2024-12-16 05:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_assignmentsubmission'),
        ('teacher', '0007_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentsubmission',
            name='assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='teacher.assignment'),
        ),
        migrations.AlterField(
            model_name='assignmentsubmission',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='student.student'),
        ),
    ]
