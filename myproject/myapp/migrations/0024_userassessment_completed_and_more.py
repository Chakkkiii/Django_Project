# Generated by Django 4.2.7 on 2024-02-23 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_remove_course_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='userassessment',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='userassessment',
            unique_together={('user', 'course', 'week')},
        ),
    ]
