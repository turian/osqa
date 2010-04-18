import startup

import os.path
from django.conf.urls.defaults import *
from django.contrib import admin
from forum import views as app
from forum.feed import RssLastestQuestionsFeed
from forum.sitemap import QuestionsSitemap
from django.utils.translation import ugettext as _
import logging

admin.autodiscover()
feeds = {
    'rss': RssLastestQuestionsFeed
}
sitemaps = {
    'questions': QuestionsSitemap
}

APP_PATH = os.path.dirname(__file__)
urlpatterns = patterns('',
    url(r'^$', app.readers.index, name='index'),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}, name='sitemap'),
    #(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/images/favicon.ico'}),
    #(r'^favicon\.gif$', 'django.views.generic.simple.redirect_to', {'url': '/media/images/favicon.gif'}),
    (r'^favicon\.ico$', app.meta.favicon),
    url(r'^m/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(APP_PATH,'skins').replace('\\','/')},
        name='osqa_media',
    ),
    url(r'^%s(?P<path>.*)$' % _('upfiles/'), 'django.views.static.serve',
        {'document_root': os.path.join(APP_PATH,'upfiles').replace('\\','/')},
        name='uploaded_file',
    ),
    #url(r'^%s/$' % _('signin/'), 'django_authopenid.views.signin', name='signin'),
    url(r'^%s$' % _('about/'), app.meta.about, name='about'),
    url(r'^%s$' % _('faq/'), app.meta.faq, name='faq'),
    url(r'^%s$' % _('privacy/'), app.meta.privacy, name='privacy'),
    url(r'^%s$' % _('logout/'), app.meta.logout, name='logout'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('answers/'), _('edit/')), app.writers.edit_answer, name='edit_answer'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('answers/'), _('revisions/')), app.readers.revisions, name='answer_revisions'),
    url(r'^%s$' % _('questions/'), app.readers.questions, name='questions'),
    url(r'^%s%s$' % (_('questions/'), _('ask/')), app.writers.ask, name='ask'),
    url(r'^%s%s$' % (_('questions/'), _('unanswered/')), app.readers.unanswered, name='unanswered'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('edit/')), app.writers.edit_question, name='edit_question'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('close/')), app.commands.close, name='close'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('reopen/')), app.commands.reopen, name='reopen'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('answer/')), app.writers.answer, name='answer'),

    url(r'^%s(?P<id>\d+)/(?P<vote_type>[a-z]+)/' % _('vote/'), app.commands.vote_post, name='vote_post'),
    url(r'^%s(?P<id>\d+)/$' % _('like_comment/'), app.commands.like_comment, name="like_comment"),
    url(r'^%s(?P<id>\d+)/' % _('comment/'), app.commands.comment, name='comment'),
    url(r'^%s(?P<id>\d+)/$' % _('delete_comment/'), app.commands.delete_comment, name="delete_comment"),
    url(r'^%s(?P<id>\d+)/$' % _('accept_answer/'), app.commands.accept_answer, name="accept_answer"),
    url(r'^%s(?P<id>\d+)/$' % _('mark_favorite/'), app.commands.mark_favorite, name="mark_favorite"),
    url(r'^%s(?P<id>\d+)/' % _('flag/'), app.commands.flag_post, name='flag_post'),
    url(r'^%s(?P<id>\d+)/' % _('delete/'), app.commands.delete_post, name='delete_post'),
    url(r'^%s(?P<id>\d+)/$' % _('subscribe/'), app.commands.subscribe, name="subscribe"),

    url(r'^%s(?P<id>\d+)/%s$' % (_('questions/'), _('revisions/')), app.readers.revisions, name='question_revisions'),
    url(r'^%s$' % _('command/'), app.commands.ajax_command, name='call_ajax'),

    #place general question item in the end of other operations
    url(r'^%s(?P<id>\d+)/(?P<slug>[\w-]*)$' % _('question/'), app.readers.question, name='question'),
    url(r'^%s$' % _('tags/'), app.readers.tags, name='tags'),
    url(r'^%s(?P<tag>[^/]+)/$' % _('tags/'), app.readers.tag, name='tag_questions'),

    url(r'^%s%s(?P<tag>[^/]+)/$' % (_('mark-tag/'),_('interesting/')), app.commands.mark_tag, \
                                kwargs={'reason':'good','action':'add'}, \
                                name='mark_interesting_tag'),

    url(r'^%s%s(?P<tag>[^/]+)/$' % (_('mark-tag/'),_('ignored/')), app.commands.mark_tag, \
                                kwargs={'reason':'bad','action':'add'}, \
                                name='mark_ignored_tag'),

    url(r'^%s(?P<tag>[^/]+)/$' % _('unmark-tag/'), app.commands.mark_tag, \
                                kwargs={'action':'remove'}, \
                                name='mark_ignored_tag'),



    url(r'^%s$' % _('users/'),app.users.users, name='users'),
    url(r'^%s(?P<id>\d+)/$' % _('moderate-user/'), app.users.moderate_user, name='moderate_user'),
    url(r'^%s(?P<id>\d+)/%s$' % (_('users/'), _('edit/')), app.users.edit_user, name='edit_user'),

    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (_('users/'), _('subscriptions/')), app.users.user_subscriptions, name='user_subscriptions'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (_('users/'), _('favorites/')), app.users.user_favorites, name='user_favorites'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (_('users/'), _('reputation/')), app.users.user_reputation, name='user_reputation'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (_('users/'), _('votes/')), app.users.user_votes, name='user_votes'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/%s$' % (_('users/'), _('recent/')), app.users.user_recent, name='user_recent'),
    url(r'^%s(?P<id>\d+)/(?P<slug>.+)/$' % _('users/'), app.users.user_stats, name='user_profile'),
    
    url(r'^%s$' % _('badges/'),app.meta.badges, name='badges'),
    url(r'^%s(?P<id>\d+)//*' % _('badges/'), app.meta.badge, name='badge'),
    url(r'^%s%s$' % (_('messages/'), _('markread/')),app.commands.read_message, name='read_message'),
    # (r'^admin/doc/' % _('admin/doc'), include('django.contrib.admindocs.urls')),
    url(r'^%s(.*)' % _('nimda/'), admin.site.root, name='osqa_admin'),
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}, name='feeds'),
    url(r'^%s$' % _('upload/'), app.writers.upload, name='upload'),
    url(r'^%s$' % _('search/'), app.readers.search, name='search'),
    url(r'^%s$' % _('feedback/'), app.meta.feedback, name='feedback'),

    (r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^%s%s$' % (_('account/'), _('signin/')), app.auth.signin_page, name='auth_signin'),
    url(r'^%s%s$' % (_('account/'), _('signout/')), app.auth.signout, name='user_signout'),
    url(r'^%s%s(?P<action>\w+)/$' % (_('account/'), _('signin/')), app.auth.signin_page, name='auth_action_signin'),
    url(r'^%s(?P<provider>\w+)/%s$' % (_('account/'), _('signin/')), app.auth.prepare_provider_signin, name='auth_provider_signin'),
    url(r'^%s(?P<provider>\w+)/%s$' % (_('account/'), _('done/')), app.auth.process_provider_signin, name='auth_provider_done'),
    url(r'^%s%s$' % (_('account/'), _('register/')), app.auth.external_register, name='auth_external_register'),
    url(r'^%s%s(?P<user>\d+)/(?P<code>.+)/$' % (_('account/'), _('validate/')),  app.auth.validate_email, name="auth_validate_email"),
    url(r'^%s%s$' % (_('account/'), _('tempsignin/')),  app.auth.request_temp_login, name="auth_request_tempsignin"),
    url(r'^%s%s(?P<user>\d+)/(?P<code>.+)/$' % (_('account/'), _('tempsignin/')),  app.auth.temp_signin, name="auth_tempsignin"),
    url(r'^%s%s$' % (_('account/'), _('authsettings/')), app.auth.auth_settings, name='user_authsettings'),
    url(r'^%s%s(?P<id>\d+)/%s$' % (_('account/'), _('providers/'),  _('remove/')), app.auth.remove_external_provider, name='user_remove_external_provider'),
    url(r'^%s%s%s$' % (_('account/'), _('providers/'),  _('add/')), app.auth.signin_page, name='user_add_external_provider'),


    url(r'^%s$' % _('admin/'), app.admin.index, name="admin_index"),
    url(r'^%s%s$' % (_('admin/'), _('denormalize/')), app.admin.recalculate_denormalized, name="admin_denormalize"),
    url(r'^%s%s$' % (_('admin/'), _('go_bootstrap/')), app.admin.go_bootstrap, name="admin_go_bootstrap"),
    url(r'^%s%s$' % (_('admin/'), _('go_defaults/')), app.admin.go_defaults, name="admin_go_defaults"),
    url(r'^%s(?P<set_name>\w+)/$' % _('admin/'), app.admin.settings_set, name="admin_set"),

    url(r'^feeds/rss/$', RssLastestQuestionsFeed, name="latest_questions_feed"),
)

from forum.modules import get_modules_script

module_patterns = get_modules_script('urls')

for pattern_file in module_patterns:
    pattern = getattr(pattern_file, 'urlpatterns', None)
    if pattern:
        urlpatterns += pattern

