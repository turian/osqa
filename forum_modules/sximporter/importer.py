# -*- coding: utf-8 -*-

from xml.dom import minidom
from datetime import datetime
import time
import re
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from orm import orm

def getText(el):
    rc = ""
    for node in el.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc.strip()

msstrip = re.compile(r'^(.*)\.\d+')
def readTime(ts):
    noms = msstrip.match(ts)
    if noms:
        ts = noms.group(1)

    return datetime(*time.strptime(ts, '%Y-%m-%dT%H:%M:%S')[0:6])

def readEl(el):
    return dict([(n.tagName.lower(), getText(n)) for n in el.childNodes if n.nodeType == el.ELEMENT_NODE])

def readTable(dump, name):
    return [readEl(e) for e in minidom.parseString(dump.read("%s.xml" % name)).getElementsByTagName('row')]

class UnknownUser(object):
    counter = 0
    def __init__(self):
        UnknownUser.counter += 1
        self.number = UnknownUser.counter

    def __str__(self):
        return _("Unknown user %(number)d") % {'number': self.number}

    def __unicode__(self):
        return self.__str__()

    def encode(self, *args):
        return self.__str__()

class IdMapper(dict):
    def __getitem__(self, key):
        key = int(key)
        return super(IdMapper, self).get(key, 1)

    def __setitem__(self, key, value):
        super(IdMapper, self).__setitem__(int(key), int(value))

openidre = re.compile('^https?\:\/\/')
def userimport(dump, options):
    users = readTable(dump, "Users")

    user_by_name = {}
    uidmapper = IdMapper()
    merged_users = []

    owneruid = options.get('owneruid', None)
    #check for empty values
    if not owneruid:
        owneruid = None

    for sxu in users:
        create = True

        if sxu.get('id') == '-1':
            continue

        if int(sxu.get('id')) == int(owneruid):
            osqau = orm.User.objects.get(id=1)
            uidmapper[owneruid] = 1
            uidmapper[-1] = 1
            create = False
        else:
            username = sxu.get('displayname', sxu.get('displaynamecleaned', sxu.get('realname', UnknownUser())))

            if not isinstance(username, UnknownUser) and username in user_by_name:
                #if options.get('mergesimilar', False) and sxu.get('email', 'INVALID') == user_by_name[username].email:
                #    osqau = user_by_name[username]
                #    create = False
                #    uidmapper[sxu.get('id')] = osqau.id
                #else:
                inc = 1
                while ("%s %d" % (username, inc)) in user_by_name:
                    inc += 1

                username = "%s %d" % (username, inc)

        sxbadges = sxu.get('badgesummary', None)
        badges = {'1':'0','2':'0','3':'0'}

        if sxbadges:
            badges.update(dict([b.split('=') for b in sxbadges.split()]))

        if create:
            osqau = orm.User(
                id           = sxu.get('id'),
                username     = unicode(username),
                password     = '!',
                email        = sxu.get('email', ''),
                is_superuser = sxu.get('usertypeid') == '5',
                is_staff     = sxu.get('usertypeid') == '4',
                is_active    = True,
                date_joined  = readTime(sxu.get('creationdate')),
                about         = sxu.get('aboutme', ''),
                date_of_birth = sxu.get('birthday', None) and readTime(sxu['birthday']) or None,
                email_isvalid = int(sxu.get('usertypeid')) > 2,
                website       = sxu.get('websiteurl', ''),
                reputation    = int(sxu.get('reputation')),
                gold          = int(badges['1']),
                silver        = int(badges['2']),
                bronze        = int(badges['3']),
                real_name     = sxu.get('realname', ''),
            )

            osqau.save()

            try:
                orm.SubscriptionSettings.objects.get(user=osqau)
            except:
                s = orm.SubscriptionSettings(user=osqau)
                s.save()

            uidmapper[osqau.id] = osqau.id
        else:
            new_about = sxu.get('aboutme', None)
            if new_about and osqau.about != new_about:
                if osqau.about:
                    osqau.about = "%s\n|\n%s" % (osqau.about, new_about)
                else:
                    osqau.about = new_about

            osqau.username = sxu.get('displayname', sxu.get('displaynamecleaned', sxu.get('realname', UnknownUser())))
            osqau.email = sxu.get('email', '')
            osqau.reputation += int(sxu.get('reputation'))
            osqau.gold += int(badges['1'])
            osqau.silver += int(badges['2'])
            osqau.bronze += int(badges['3'])

            merged_users.append(osqau.id)
            osqau.save()

        user_by_name[osqau.username] = osqau

        openid = sxu.get('openid', None)
        if openid and openidre.match(openid):
            assoc = orm.AuthKeyUserAssociation(user=osqau, key=openid, provider="openidurl")
            assoc.save()

    if uidmapper[-1] == -1:
        uidmapper[-1] = 1

    return (uidmapper, merged_users)

def tagsimport(dump, uidmap):
    tags = readTable(dump, "Tags")

    tagmap = {}

    for sxtag in tags:
        otag = orm.Tag(
            id = int(sxtag['id']),
            name = sxtag['name'],
            used_count = int(sxtag['count']),
            created_by_id = uidmap[sxtag.get('userid', 1)],
        )
        otag.save()

        tagmap[otag.name] = otag

    return tagmap

def postimport(dump, uidmap, tagmap):
    history = {}
    accepted = {}
    all = {}

    for h in readTable(dump, "PostHistory"):
        if not history.get(h.get('postid'), None):
            history[h.get('postid')] = []

        history[h.get('postid')].append(h)

    posts = readTable(dump, "Posts")

    for sxpost in posts:
        postclass = sxpost.get('posttypeid') == '1' and orm.Question or orm.Answer

        post = postclass(
            id = sxpost['id'],
            added_at = readTime(sxpost['creationdate']),
            body = sxpost['body'],
            score = sxpost.get('score', 0),
            vote_up_count = 0,
            vote_down_count = 0
        )

        if sxpost.get('deletiondate', None):
            post.deleted = True
            post.deleted_at = readTime(sxpost['deletiondate'])
            post.author_id = 1
        else:
            post.author_id = uidmap[sxpost['owneruserid']]

        if sxpost.get('lasteditoruserid', None):
            post.last_edited_by_id = uidmap[sxpost.get('lasteditoruserid')]
            post.last_edited_at = readTime(sxpost['lasteditdate'])

        if sxpost.get('communityowneddate', None):
            post.wiki = True
            post.wikified_at = readTime(sxpost['communityowneddate'])

        if sxpost.get('posttypeid') == '1': #question
            post.node_type = "question"
            post.title = sxpost['title']

            tagnames = sxpost['tags'].replace(u'ö', '-').replace(u'é', '').replace(u'à', '')
            post.tagnames = tagnames

            post.view_count = sxpost.get('viewcount', 0)
            post.favourite_count = sxpost.get('favoritecount', 0)
            post.answer_count = sxpost.get('answercount', 0)

            if sxpost.get('lastactivityuserid', None):
                post.last_activity_by_id = uidmap[sxpost['lastactivityuserid']]
                post.last_activity_at = readTime(sxpost['lastactivitydate'])

            if sxpost.get('closeddate', None):
                post.closed = True
                post.closed_by_id = 1
                post.closed_at = datetime.now()

            if sxpost.get('acceptedanswerid', None):
                post.accepted_answer_id = int(sxpost.get('acceptedanswerid'))
                accepted[int(sxpost.get('acceptedanswerid'))] = post

        else:
            post.node_type = "answer"
            post.parent_id = sxpost['parentid']

            if int(post.id) in accepted:
                post.accepted = True
                post.accepted_at = datetime.now()
                post.accepted_by_id = accepted[int(post.id)].author_id

        all[int(post.id)] = post

    return all

def comment_import(dump, uidmap, posts):
    comments = readTable(dump, "PostComments")
    currid = max(posts.keys())
    mapping = {}

    for sxc in comments:
        currid += 1
        oc = orm.Node(
            id = currid,
            node_type = "comment",
            added_at = readTime(sxc['creationdate']),
            author_id = uidmap[sxc.get('userid', 1)],
            body = sxc['text'],
            parent_id = sxc.get('postid'),
            vote_up_count = 0,
            vote_down_count = 0
        )

        if sxc.get('deletiondate', None):
            oc.deleted = True
            oc.deleted_at = readTime(sxc['deletiondate'])
            oc.deleted_by_id = uidmap[sxc['deletionuserid']]
            oc.author_id = uidmap[sxc['deletionuserid']]
        else:
            oc.author_id = uidmap[sxc.get('userid', 1)]


        posts[oc.id] = oc
        mapping[int(sxc['id'])] = int(oc.id)

    return posts, mapping


def save_posts(posts, tagmap):
    for post in posts.values():
        post.save()

        if post.node_type == "question":
            tags = filter(lambda t: t is not None, [tagmap.get(n, None) for n in post.tagnames.split()])
            post.tagnames = " ".join([t.name for t in tags]).strip()
            post.tags = tags

        create_and_activate_revision(post)


def create_and_activate_revision(post):
    rev = orm.NodeRevision(
        author_id = post.author_id,
        body = post.body,
        node_id = post.id,
        revised_at = post.added_at,
        revision = 1,
        summary = 'Initial revision',
        tagnames = post.tagnames,
        title = post.title,
    )

    rev.save()
    post.active_revision_id = rev.id
    post.save()


def post_vote_import(dump, uidmap, posts):
    votes = readTable(dump, "Posts2Votes")

    for sxv in votes:
        if sxv['votetypeid'] in ('2', '3'):
            ov = orm.Vote(
                node_id = sxv['postid'],
                user_id = uidmap[sxv['userid']],
                voted_at = readTime(sxv['creationdate']),
                vote = sxv['votetypeid'] == '2' and 1 or -1,
            )

            if sxv['votetypeid'] == '2':
                posts[int(sxv['postid'])].vote_up_count += 1
            else:
                posts[int(sxv['postid'])].vote_down_count += 1

            ov.save()

def comment_vote_import(dump, uidmap, comments, posts):
    votes = readTable(dump, "Comments2Votes")

    for sxv in votes:
        if sxv['votetypeid'] in ('2', '3'):
            ov = orm.Vote(
                node_id = comments[int(sxv['postcommentid'])],
                user_id = uidmap[sxv['userid']],
                voted_at = readTime(sxv['creationdate']),
                vote = sxv['votetypeid'] == '2' and 1 or -1,
            )

            if sxv['votetypeid'] == '2':
                posts[comments[int(sxv['postcommentid'])]].vote_up_count += 1
            else:
                posts[comments[int(sxv['postcommentid'])]].vote_down_count += 1

            ov.save()



def badges_import(dump, uidmap):
    node_ctype = orm['contenttypes.contenttype'].objects.get(name='node')
    obadges = dict([(b.slug, b) for b in orm.Badge.objects.all()])
    sxbadges = dict([(int(b['id']), b) for b in readTable(dump, "Badges")])

    sx_to_osqa = {}

    for id, sxb in sxbadges.items():
        slug = slugify(sxb['name'].replace('&', 'and'))
        if slug in obadges:
            sx_to_osqa[id] = obadges[slug]
        else:
            osqab = orm.Badge(
                name = sxb['name'],
                slug = slugify(sxb['name']),
                description = sxb['description'],
                multiple = sxb.get('single', 'false') == 'false',
                awarded_count = 0,
                type = sxb['class']                
            )
            osqab.save()
            sx_to_osqa[id] = osqab

    sxawards = readTable(dump, "Users2Badges")
    osqaawards = []

    for sxa in sxawards:
        badge = sx_to_osqa[int(sxa['badgeid'])]
        osqaa = orm.Award(
            user_id = uidmap[sxa['userid']],
            badge = badge,
            content_type = node_ctype,
            object_id = 1
        )

        osqaawards.append(osqaa)
        badge.awarded_count += 1

    for b in sx_to_osqa.values():
        b.save()

    for a in osqaawards:
        a.save()


def reset_sequences():
    from south.db import db
    if db.backend_name == "postgres":
        db.start_transaction()
        db.execute_many(PG_SEQUENCE_RESETS)
        db.commit_transaction()

def sximport(dump, options):
    uidmap, merged_users = userimport(dump, options)
    tagmap = tagsimport(dump, uidmap)
    posts = postimport(dump, uidmap, tagmap)
    posts, comments = comment_import(dump, uidmap, posts)
    save_posts(posts, tagmap)
    post_vote_import(dump, uidmap, posts)
    comment_vote_import(dump, uidmap, comments, posts)
    for post in posts.values():
        post.save()
    badges_import(dump, uidmap)

    from south.db import db
    db.commit_transaction()

    reset_sequences()

    
    
PG_SEQUENCE_RESETS = """
SELECT setval('"auth_user_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user";
SELECT setval('"auth_user_groups_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_groups";
SELECT setval('"auth_user_user_permissions_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_user_permissions";
SELECT setval('"activity_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "activity";
SELECT setval('"forum_subscriptionsettings_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_subscriptionsettings";
SELECT setval('"forum_validationhash_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_validationhash";
SELECT setval('"forum_authkeyuserassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_authkeyuserassociation";
SELECT setval('"tag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "tag";
SELECT setval('"forum_markedtag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_markedtag";
SELECT setval('"forum_node_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_noderevision_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_noderevision";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"favorite_question_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "favorite_question";
SELECT setval('"forum_questionsubscription_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_questionsubscription";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"vote_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "vote";
SELECT setval('"flagged_item_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "flagged_item";
SELECT setval('"badge_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "badge";
SELECT setval('"award_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "award";
SELECT setval('"repute_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "repute";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_keyvalue_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_keyvalue";
SELECT setval('"forum_openidnonce_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidnonce";
SELECT setval('"forum_openidassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidassociation";
"""


    
    