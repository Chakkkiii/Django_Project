# Generated by Django 4.2.7 on 2024-02-09 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_reviewrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='categories',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='certi',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='course',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='course',
            name='requirements',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='course',
            name='skill_level',
            field=models.CharField(blank=True, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], max_length=20),
        ),
    ]
