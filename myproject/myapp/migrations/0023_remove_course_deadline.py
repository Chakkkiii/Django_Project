# Generated by Django 4.2.7 on 2024-02-09 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_course_categories_course_certi_course_deadline_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='deadline',
        ),
    ]