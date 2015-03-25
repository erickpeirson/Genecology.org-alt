# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Appellation',
            fields=[
                ('annotation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='main.Annotation')),
                ('start_position', models.IntegerField(null=True, blank=True)),
                ('end_position', models.IntegerField(null=True, blank=True)),
                ('interpretation', models.ForeignKey(related_name='representations', to='concepts.Concept')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.annotation',),
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdgeBundle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('contains', models.ManyToManyField(related_name='in_bundles', to='main.Edge')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdgePosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('x_source', models.IntegerField()),
                ('x_target', models.IntegerField()),
                ('y_source', models.IntegerField()),
                ('y_target', models.IntegerField()),
                ('z', models.IntegerField(default=0)),
                ('width', models.IntegerField(default=1)),
                ('describes', models.ForeignKey(to='main.Edge')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodeBundle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('contains', models.ManyToManyField(related_name='in_bundles', to='main.Node')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NodePosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField(default=0)),
                ('size', models.FloatField(default=1)),
                ('describes_by_id', models.IntegerField()),
                ('describes', models.ForeignKey(to='main.Node')),
                ('part_of', models.ForeignKey(to='main.Layout')),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('annotation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='main.Annotation')),
                ('start', models.DateField(null=True, blank=True)),
                ('occur', models.DateField(null=True, blank=True)),
                ('end', models.DateField(null=True, blank=True)),
                ('predicate', models.ForeignKey(related_name='relations_with', to='main.Appellation')),
                ('source', models.ForeignKey(related_name='relations_from', to='main.Appellation')),
                ('target', models.ForeignKey(related_name='relations_to', to='main.Appellation')),
            ],
            options={
                'abstract': False,
            },
            bases=('main.annotation',),
        ),
        migrations.CreateModel(
            name='Researcher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, null=True, blank=True)),
                ('link', models.URLField(max_length=255, null=True, blank=True)),
                ('photo', models.FileField(null=True, upload_to=b'', blank=True)),
                ('bio', models.TextField(null=True, blank=True)),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('uri', models.CharField(max_length=255)),
                ('content_url', models.URLField(max_length=255, null=True, blank=True)),
                ('content', models.TextField()),
                ('length', models.IntegerField(default=0)),
                ('restricted', models.BooleanField(default=True)),
                ('creators', models.ManyToManyField(to='concepts.Concept')),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='nodebundle',
            name='evidence',
            field=models.ManyToManyField(to='main.Annotation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodebundle',
            name='part_of',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodebundle',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nodebundle',
            name='represents',
            field=models.ForeignKey(to='concepts.Concept'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='evidence',
            field=models.ManyToManyField(to='main.Annotation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='part_of',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='represents',
            field=models.ForeignKey(to='concepts.Concept'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='layout',
            name='describes',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='layout',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgeposition',
            name='part_of',
            field=models.ForeignKey(to='main.Layout'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgeposition',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgebundle',
            name='evidence',
            field=models.ManyToManyField(to='main.Annotation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgebundle',
            name='part_of',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgebundle',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edgebundle',
            name='represents',
            field=models.ForeignKey(to='concepts.Concept'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='evidence',
            field=models.ManyToManyField(to='main.Annotation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='part_of',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='represents',
            field=models.ForeignKey(to='concepts.Concept'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='source',
            field=models.ForeignKey(related_name='edges_from', to='main.Node'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='target',
            field=models.ForeignKey(related_name='edges_to', to='main.Node'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='appellation',
            name='text',
            field=models.ForeignKey(related_name='annotations', to='main.Text'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotation',
            name='in_accession',
            field=models.ForeignKey(to='main.Accession'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotation',
            name='made_by',
            field=models.ForeignKey(related_name='contributions', blank=True, to='main.Researcher', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='annotation',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accession',
            name='part_of',
            field=models.ForeignKey(to='main.Network'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='accession',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
