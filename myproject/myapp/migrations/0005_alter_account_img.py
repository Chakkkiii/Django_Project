# Generated by Django 4.2.7 on 2023-12-08 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_course_course_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='img',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='pics'),
        ),
    ]
