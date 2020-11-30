# Generated by Django 2.2.14 on 2020-11-29 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('slot_order', models.IntegerField(null=True)),
                ('started', models.DateField(null=True)),
                ('completed', models.DateField(null=True)),
            ],
            options={
                'db_table': 'operations',
                'ordering': ['slot_order'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('color', models.CharField(default='', max_length=20)),
            ],
            options={
                'db_table': 'projects',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('completed', models.BooleanField(default=False)),
                ('order', models.IntegerField()),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.Operation')),
            ],
            options={
                'db_table': 'tasks',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('order', models.IntegerField()),
                ('operation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slot_active', to='core.Operation')),
            ],
            options={
                'db_table': 'slots',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='ProjectOperationLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_order', models.IntegerField()),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Operation')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project')),
            ],
            options={
                'db_table': 'project_operation_links',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='operations',
            field=models.ManyToManyField(related_name='projects', through='core.ProjectOperationLink', to='core.Operation'),
        ),
        migrations.AddField(
            model_name='operation',
            name='slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='core.Slot'),
        ),
    ]
