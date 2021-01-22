# Generated by Django 2.2.14 on 2021-01-21 18:20

from django.db import migrations, models
import django.db.models.deletion
import time


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_slot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default='')),
                ('color', models.CharField(max_length=9)),
                ('status', models.IntegerField(choices=[(1, 'Not Started'), (2, 'Active'), (3, 'Maintenance'), (4, 'Completed'), (5, 'Abandoned')], default=2)),
                ('creation_time', models.IntegerField(default=time.time)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='core.User')),
            ],
            options={
                'db_table': 'projects',
                'ordering': ['creation_time'],
            },
        ),
    ]