# Generated by Django 2.2.14 on 2020-12-02 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='completed',
            field=models.IntegerField(default=None, null=True),
        ),
    ]