# Generated by Django 4.2.7 on 2023-12-08 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_week',
            field=models.IntegerField(choices=[(1, 'Week 2'), (2, 'Week 4'), (3, 'Week 8')]),
        ),
    ]
