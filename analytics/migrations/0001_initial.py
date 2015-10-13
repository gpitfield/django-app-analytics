# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_id', models.CharField(max_length=60, db_index=True)),
                ('platform', models.CharField(max_length=20, null=True, db_index=True)),
                ('analytics', models.CharField(max_length=5000, null=True, blank=True)),
                ('active', models.BooleanField(default=False)),
                ('complete', models.BooleanField(default=False, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Analytic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_id', models.CharField(max_length=100, db_index=True)),
                ('device_uuid', uuidfield.fields.UUIDField(db_index=True, max_length=32, null=True, blank=True)),
                ('platform', models.CharField(default=b'iOS', max_length=20, db_index=True)),
                ('device_model', models.CharField(max_length=100, null=True, blank=True)),
                ('app_version', models.CharField(default=b'1.1', max_length=8, db_index=True)),
                ('event', models.CharField(max_length=100, db_index=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AnalyticsDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('device_id', models.CharField(unique=True, max_length=60, db_index=True)),
                ('first_seen', models.DateTimeField()),
                ('beta_device', models.BooleanField(default=False)),
                ('platform', models.CharField(default=b'iOS', max_length=20, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.IntegerField(default=1)),
                ('count', models.IntegerField(default=0)),
                ('locked', models.BooleanField(default=False, db_index=True)),
                ('index_date', models.DateField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='CohortSlice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index_date', models.DateField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('count', models.IntegerField(default=0)),
                ('analytics', models.CharField(max_length=5000, null=True, blank=True)),
                ('complete', models.BooleanField(default=False, db_index=True)),
                ('cohort', models.ForeignKey(to='analytics.Cohort')),
            ],
        ),
        migrations.CreateModel(
            name='ContentSlice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.IntegerField(default=1)),
                ('index_date', models.DateField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('analytics', models.CharField(max_length=5000, null=True, blank=True)),
                ('complete', models.BooleanField(default=False, db_index=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contentslice',
            unique_together=set([('size', 'index_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='cohort',
            unique_together=set([('size', 'index_date')]),
        ),
        migrations.AlterIndexTogether(
            name='cohort',
            index_together=set([('size', 'index_date')]),
        ),
        migrations.AddField(
            model_name='analyticsdevice',
            name='cohorts',
            field=models.ManyToManyField(to='analytics.Cohort'),
        ),
        migrations.AddField(
            model_name='aggregatedevice',
            name='cohort_slice',
            field=models.ForeignKey(to='analytics.CohortSlice'),
        ),
        migrations.AlterUniqueTogether(
            name='cohortslice',
            unique_together=set([('cohort', 'index_date')]),
        ),
        migrations.AlterIndexTogether(
            name='cohortslice',
            index_together=set([('cohort', 'index_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='aggregatedevice',
            unique_together=set([('cohort_slice', 'device_id')]),
        ),
        migrations.AlterIndexTogether(
            name='aggregatedevice',
            index_together=set([('cohort_slice', 'device_id')]),
        ),
    ]
