# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'NodeRevision'
        db.create_table('forum_noderevision', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='revisions', to=orm['forum.Node'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='noderevisions', to=orm['forum.User'])),
            ('tagnames', self.gf('django.db.models.fields.CharField')(max_length=125)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('revised_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('forum', ['NodeRevision'])

        # Deleting field 'Vote.object_id'
        db.delete_column(u'vote', 'object_id')

        # Deleting field 'Vote.content_type'
        db.delete_column(u'vote', 'content_type_id')

        # Deleting field 'Comment.object_id'
        db.delete_column(u'comment', 'object_id')

        # Deleting field 'Comment.content_type'
        db.delete_column(u'comment', 'content_type_id')

        # Deleting field 'FlaggedItem.object_id'
        db.delete_column(u'flagged_item', 'object_id')

        # Deleting field 'FlaggedItem.content_type'
        db.delete_column(u'flagged_item', 'content_type_id')
    
    
    def backwards(self, orm):
        
        # Deleting model 'NodeRevision'
        db.delete_table('forum_noderevision')

        # Adding field 'Vote.object_id'
        db.add_column(u'vote', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)

        # Adding field 'Vote.content_type'
        db.add_column(u'vote', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'Comment.object_id'
        db.add_column(u'comment', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)

        # Adding field 'Comment.content_type'
        db.add_column(u'comment', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'FlaggedItem.object_id'
        db.add_column(u'flagged_item', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=1), keep_default=False)

        # Adding field 'FlaggedItem.content_type'
        db.add_column(u'flagged_item', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['contenttypes.ContentType']), keep_default=False)
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forum.activity': {
            'Meta': {'object_name': 'Activity', 'db_table': "u'activity'"},
            'active_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'activity_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_auditted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.anonymousanswer': {
            'Meta': {'object_name': 'AnonymousAnswer'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'anonymous_answers'", 'to': "orm['forum.Question']"}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'forum.anonymousquestion': {
            'Meta': {'object_name': 'AnonymousQuestion'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_addr': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'forum.answer': {
            'Meta': {'object_name': 'Answer', 'db_table': "u'answer'"},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'accepted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'accepted_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']", 'null': 'True'}),
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['forum.User']"}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_answers'", 'null': 'True', 'to': "orm['forum.User']"}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_edited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_answers'", 'null': 'True', 'to': "orm['forum.User']"}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['forum.Node']", 'unique': 'True', 'null': 'True'}),
            'offensive_flag_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['forum.Question']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_down_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_up_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wikified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'forum.answerrevision': {
            'Meta': {'object_name': 'AnswerRevision', 'db_table': "u'answer_revision'"},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Answer']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answerrevisions'", 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'forum.authkeyuserassociation': {
            'Meta': {'object_name': 'AuthKeyUserAssociation'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'auth_keys'", 'to': "orm['forum.User']"})
        },
        'forum.award': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'user', 'badge'),)", 'object_name': 'Award', 'db_table': "u'award'"},
            'awarded_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'award_badge'", 'to': "orm['forum.Badge']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notified': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'awards'", 'to': "orm['forum.User']"})
        },
        'forum.badge': {
            'Meta': {'unique_together': "(('name', 'type'),)", 'object_name': 'Badge', 'db_table': "u'badge'"},
            'awarded_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'awarded_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'badges'", 'through': "'Award'", 'to': "orm['forum.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'forum.comment': {
            'Meta': {'object_name': 'Comment', 'db_table': "u'comment'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_comments'", 'null': 'True', 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'liked_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'comments_liked'", 'through': "'LikedComment'", 'to': "orm['forum.User']"}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['forum.User']"})
        },
        'forum.favoritequestion': {
            'Meta': {'unique_together': "(('question', 'user'),)", 'object_name': 'FavoriteQuestion', 'db_table': "u'favorite_question'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_favorite_questions'", 'to': "orm['forum.User']"})
        },
        'forum.flaggeditem': {
            'Meta': {'object_name': 'FlaggedItem', 'db_table': "u'flagged_item'"},
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'flagged_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flaggeditems'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'flaggeditems'", 'to': "orm['forum.User']"})
        },
        'forum.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'value': ('forum.models.utils.PickledObjectField', [], {})
        },
        'forum.likedcomment': {
            'Meta': {'object_name': 'LikedComment'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Comment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.markedtag': {
            'Meta': {'object_name': 'MarkedTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_selections'", 'to': "orm['forum.Tag']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tag_selections'", 'to': "orm['forum.User']"})
        },
        'forum.node': {
            'Meta': {'object_name': 'Node'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'to': "orm['forum.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_nodes'", 'null': 'True', 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_edited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_nodes'", 'null': 'True', 'to': "orm['forum.User']"}),
            'node_type': ('django.db.models.fields.CharField', [], {'default': "'node'", 'max_length': '16'}),
            'offensive_flag_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'childs'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'nodes'", 'to': "orm['forum.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'vote_down_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_up_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'forum.noderevision': {
            'Meta': {'unique_together': "(('node', 'revision'),)", 'object_name': 'NodeRevision'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'noderevisions'", 'to': "orm['forum.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Node']"}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'forum.question': {
            'Meta': {'object_name': 'Question', 'db_table': "u'question'"},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'answer_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'answer_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questions'", 'to': "orm['forum.User']"}),
            'close_reason': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'closed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'closed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'closed_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'comment_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'favorited_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'favorite_questions'", 'through': "'FavoriteQuestion'", 'to': "orm['forum.User']"}),
            'favourite_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'followed_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followed_questions'", 'to': "orm['forum.User']"}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_activity_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_activity_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'last_active_in_questions'", 'to': "orm['forum.User']"}),
            'last_edited_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_edited_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_edited_questions'", 'null': 'True', 'to': "orm['forum.User']"}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['forum.Node']", 'unique': 'True', 'null': 'True'}),
            'offensive_flag_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'questions'", 'to': "orm['forum.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'view_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_down_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'vote_up_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'wiki': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wikified_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'forum.questionrevision': {
            'Meta': {'object_name': 'QuestionRevision', 'db_table': "u'question_revision'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'questionrevisions'", 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'revisions'", 'to': "orm['forum.Question']"}),
            'revised_at': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'tagnames': ('django.db.models.fields.CharField', [], {'max_length': '125'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'forum.questionsubscription': {
            'Meta': {'object_name': 'QuestionSubscription'},
            'auto_subscription': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_view': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 4, 14, 12, 14, 26, 755000)'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.repute': {
            'Meta': {'object_name': 'Repute', 'db_table': "u'repute'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.Question']"}),
            'reputation_type': ('django.db.models.fields.SmallIntegerField', [], {}),
            'reputed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reputes'", 'to': "orm['forum.User']"}),
            'user_previous_rep': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        'forum.subscriptionsettings': {
            'Meta': {'object_name': 'SubscriptionSettings'},
            'all_questions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'all_questions_watched_tags': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_joins': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'new_question': ('django.db.models.fields.CharField', [], {'default': "'d'", 'max_length': '1'}),
            'new_question_watched_tags': ('django.db.models.fields.CharField', [], {'default': "'i'", 'max_length': '1'}),
            'notify_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notify_answers': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'notify_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'notify_comments_own_post': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'notify_reply_to_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_answered': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_asked': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'questions_commented': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'questions_viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'subscribed_questions': ('django.db.models.fields.CharField', [], {'default': "'i'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'subscription_settings'", 'unique': 'True', 'to': "orm['forum.User']"})
        },
        'forum.tag': {
            'Meta': {'object_name': 'Tag', 'db_table': "u'tag'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_tags'", 'to': "orm['forum.User']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deleted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'deleted_tags'", 'null': 'True', 'to': "orm['forum.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marked_by': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'marked_tags'", 'through': "'MarkedTag'", 'to': "orm['forum.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'used_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'forum.user': {
            'Meta': {'object_name': 'User', '_ormbases': ['auth.User']},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bronze': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email_isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email_key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'gold': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'hide_ignored_questions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'questions_per_page': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reputation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'silver': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'forum.validationhash': {
            'Meta': {'unique_together': "(('user', 'type'),)", 'object_name': 'ValidationHash'},
            'expiration': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 4, 15, 12, 14, 35, 357000)'}),
            'hash_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seed': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['forum.User']"})
        },
        'forum.vote': {
            'Meta': {'object_name': 'Vote', 'db_table': "u'vote'"},
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'null': 'True', 'to': "orm['forum.Node']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['forum.User']"}),
            'vote': ('django.db.models.fields.SmallIntegerField', [], {}),
            'voted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }
    
    complete_apps = ['forum']
