# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cluster'
        db.create_table('cbmonitor_cluster', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('master_node', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('rest_username', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('rest_password', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
        ))
        db.send_create_signal('cbmonitor', ['Cluster'])

        # Adding model 'Server'
        db.create_table('cbmonitor_server', (
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Cluster'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=80, primary_key=True)),
            ('ssh_username', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('ssh_password', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('ssh_key', self.gf('django.db.models.fields.CharField')(max_length=4096, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal('cbmonitor', ['Server'])

        # Adding model 'BucketType'
        db.create_table('cbmonitor_buckettype', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=9, primary_key=True)),
        ))
        db.send_create_signal('cbmonitor', ['BucketType'])

        # Adding model 'Bucket'
        db.create_table('cbmonitor_bucket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='default', max_length=32)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Cluster'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.BucketType'])),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=11211, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('cbmonitor', ['Bucket'])

        # Adding unique constraint on 'Bucket', fields ['name', 'cluster']
        db.create_unique('cbmonitor_bucket', ['name', 'cluster_id'])

        # Adding model 'ObservableType'
        db.create_table('cbmonitor_observabletype', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True)),
        ))
        db.send_create_signal('cbmonitor', ['ObservableType'])

        # Adding model 'Observable'
        db.create_table('cbmonitor_observable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.ObservableType'])),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Cluster'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Server'], null=True, blank=True)),
            ('bucket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Bucket'], null=True, blank=True)),
            ('collector', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('cbmonitor', ['Observable'])

        # Adding unique constraint on 'Observable', fields ['name', 'cluster', 'server', 'bucket']
        db.create_unique('cbmonitor_observable', ['name', 'cluster_id', 'server_id', 'bucket_id'])

        # Adding model 'Snapshot'
        db.create_table('cbmonitor_snapshot', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, primary_key=True)),
            ('ts_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('ts_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbmonitor.Cluster'])),
        ))
        db.send_create_signal('cbmonitor', ['Snapshot'])

    def backwards(self, orm):
        # Removing unique constraint on 'Observable', fields ['name', 'cluster', 'server', 'bucket']
        db.delete_unique('cbmonitor_observable', ['name', 'cluster_id', 'server_id', 'bucket_id'])

        # Removing unique constraint on 'Bucket', fields ['name', 'cluster']
        db.delete_unique('cbmonitor_bucket', ['name', 'cluster_id'])

        # Deleting model 'Cluster'
        db.delete_table('cbmonitor_cluster')

        # Deleting model 'Server'
        db.delete_table('cbmonitor_server')

        # Deleting model 'BucketType'
        db.delete_table('cbmonitor_buckettype')

        # Deleting model 'Bucket'
        db.delete_table('cbmonitor_bucket')

        # Deleting model 'ObservableType'
        db.delete_table('cbmonitor_observabletype')

        # Deleting model 'Observable'
        db.delete_table('cbmonitor_observable')

        # Deleting model 'Snapshot'
        db.delete_table('cbmonitor_snapshot')

    models = {
        'cbmonitor.bucket': {
            'Meta': {'unique_together': "(['name', 'cluster'],)", 'object_name': 'Bucket'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Cluster']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '32'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '11211', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.BucketType']"})
        },
        'cbmonitor.buckettype': {
            'Meta': {'object_name': 'BucketType'},
            'type': ('django.db.models.fields.CharField', [], {'max_length': '9', 'primary_key': 'True'})
        },
        'cbmonitor.cluster': {
            'Meta': {'object_name': 'Cluster'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'master_node': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'rest_password': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'rest_username': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'cbmonitor.observable': {
            'Meta': {'unique_together': "(['name', 'cluster', 'server', 'bucket'],)", 'object_name': 'Observable'},
            'bucket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Bucket']", 'null': 'True', 'blank': 'True'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Cluster']"}),
            'collector': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Server']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.ObservableType']"}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'})
        },
        'cbmonitor.observabletype': {
            'Meta': {'object_name': 'ObservableType'},
            'type': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True'})
        },
        'cbmonitor.server': {
            'Meta': {'object_name': 'Server'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'primary_key': 'True'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Cluster']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'ssh_key': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'ssh_password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'ssh_username': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'cbmonitor.snapshot': {
            'Meta': {'object_name': 'Snapshot'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbmonitor.Cluster']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'primary_key': 'True'}),
            'ts_from': ('django.db.models.fields.DateTimeField', [], {}),
            'ts_to': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['cbmonitor']
