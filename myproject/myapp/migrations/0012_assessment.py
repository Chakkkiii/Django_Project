# Generated by Django 4.2.7 on 2024-01-03 12:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_delete_assessment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.IntegerField(choices=[(1, 'Week 1'), (2, 'Week 2'), (3, 'Week 3'), (4, 'Week 4'), (5, 'Week 5'), (6, 'Week 6'), (7, 'Week 7'), (8, 'Week 8')])),
                ('assessment_file', models.FileField(upload_to='assessments')),
                ('question', models.TextField()),
                ('option1', models.CharField(max_length=255)),
                ('option2', models.CharField(max_length=255)),
                ('option3', models.CharField(max_length=255)),
                ('option4', models.CharField(max_length=255)),
                ('option5', models.CharField(max_length=255)),
                ('answers', models.CharField(help_text='Enter the correct answer(s) separated by commas', max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.course')),
            ],
        ),
    ]
