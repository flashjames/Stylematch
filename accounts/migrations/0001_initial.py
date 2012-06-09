# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('accounts_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('display_on_first_page', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('profile_text', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('profile_url', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('temporary_profile_url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=36)),
            ('number_on_profile', self.gf('django.db.models.fields.BooleanField')(default=False, max_length=1)),
            ('personal_phone_number', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('salon_phone_number', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('salon_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('salon_city', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('salon_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('salon_adress', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('zip_adress', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('url_online_booking', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('show_booking_url', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('accounts', ['UserProfile'])

        # Adding model 'Service'
        db.create_table('accounts_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('price', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('display_on_profile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('accounts', ['Service'])

        # Adding model 'OpenHours'
        db.create_table('accounts_openhours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('mon', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('mon_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('tues', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('tues_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('wed', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('wed_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('thurs', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('thurs_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('fri', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('fri_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('sat', self.gf('django.db.models.fields.IntegerField')(default=480)),
            ('sat_closed', self.gf('django.db.models.fields.IntegerField')(default=1020)),
            ('sun', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('sun_closed', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal('accounts', ['OpenHours'])

        # Adding model 'Picture'
        db.create_table('accounts_picture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('image_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('display_on_profile', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('accounts', ['Picture'])

        # Adding model 'InviteCode'
        db.create_table('accounts_invitecode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('used', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invite_code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('accounts', ['InviteCode'])


    def backwards(self, orm):
        
        # Deleting model 'UserProfile'
        db.delete_table('accounts_userprofile')

        # Deleting model 'Service'
        db.delete_table('accounts_service')

        # Deleting model 'OpenHours'
        db.delete_table('accounts_openhours')

        # Deleting model 'Picture'
        db.delete_table('accounts_picture')

        # Deleting model 'InviteCode'
        db.delete_table('accounts_invitecode')


    models = {
        'accounts.invitecode': {
            'Meta': {'object_name': 'InviteCode'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'accounts.openhours': {
            'Meta': {'object_name': 'OpenHours'},
            'fri': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'fri_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mon': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'mon_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'}),
            'sat': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'sat_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'}),
            'sun': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'sun_closed': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'thurs': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'thurs_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'}),
            'tues': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'tues_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'wed': ('django.db.models.fields.IntegerField', [], {'default': '480'}),
            'wed_closed': ('django.db.models.fields.IntegerField', [], {'default': '1020'})
        },
        'accounts.picture': {
            'Meta': {'ordering': "['order']", 'object_name': 'Picture'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'display_on_profile': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.service': {
            'Meta': {'ordering': "['order']", 'object_name': 'Service'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display_on_profile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {'max_length': '6'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'display_on_first_page': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number_on_profile': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'max_length': '1'}),
            'personal_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'profile_text': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'salon_adress': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'salon_city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'salon_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'salon_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'salon_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'show_booking_url': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'temporary_profile_url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '36'}),
            'url_online_booking': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zip_adress': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']
