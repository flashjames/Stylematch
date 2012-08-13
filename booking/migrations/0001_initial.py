# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CalendarEvent'
        db.create_table('booking_calendarevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('booking', ['CalendarEvent'])


    def backwards(self, orm):
        
        # Deleting model 'CalendarEvent'
        db.delete_table('booking_calendarevent')


    models = {
        'booking.calendarevent': {
            'Meta': {'object_name': 'CalendarEvent'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['booking']
