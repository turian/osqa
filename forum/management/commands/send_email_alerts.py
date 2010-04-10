from datetime import datetime, timedelta
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _
from django.template import loader, Context, Template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from forum.models import KeyValue, Activity, User, QuestionSubscription
from forum.utils.mail import send_email
from forum import const

class QuestionRecord:
    def __init__(self, question):
        self.question = question
        self.records = []

    def log_activity(self, activity):
        self.records.append(activity)

    def get_activity_since(self, since):
        activity = [r for r in self.records if r.active_at > since]
        answers = [a for a in activity if a.activity_type == const.TYPE_ACTIVITY_ANSWER]
        comments = [a for a in activity if a.activity_type in (const.TYPE_ACTIVITY_COMMENT_QUESTION, const.TYPE_ACTIVITY_COMMENT_ANSWER)]

        accepted = [a for a in activity if a.activity_type == const.TYPE_ACTIVITY_MARK_ANSWER]

        if len(accepted):
            accepted = accepted[-1:][0]
        else:
            accepted = None

        return {
            'answers': answers,
            'comments': comments,
            'accepted': accepted,
        }


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        digest_control = self.get_digest_control()

        self.send_digest('daily', 'd', digest_control.value['LAST_DAILY'])
        digest_control.value['LAST_DAILY'] = datetime.now()

        if digest_control.value['LAST_WEEKLY'] + timedelta(days=7) <= datetime.now():
            self.send_digest('weekly', 'w', digest_control.value['LAST_WEEKLY'])
            digest_control.value['LAST_WEEKLY'] = datetime.now()

        digest_control.save()
            

    def send_digest(self, name, char_in_db, control_date):
        new_questions, question_records = self.prepare_activity(control_date)
        new_users = User.objects.filter(date_joined__gt=control_date)

        digest_subject = settings.EMAIL_SUBJECT_PREFIX + _('Daily digest')

        users = User.objects.filter(subscription_settings__enable_notifications=True)

        msgs = []

        for u in users:
            context = {
                'user': u,
                'digest_type': name,
            }

            if u.subscription_settings.member_joins == char_in_db:
                context['new_users'] = new_users
            else:
                context['new_users'] = False

            if u.subscription_settings.subscribed_questions == char_in_db:
                activity_in_subscriptions = []

                for id, r in question_records.items():
                    try:
                        subscription = QuestionSubscription.objects.get(question=r.question, user=u)

                        record = r.get_activity_since(subscription.last_view)

                        if not u.subscription_settings.notify_answers:
                            del record['answers']

                        if not u.subscription_settings.notify_comments:
                            if u.subscription_settings.notify_comments_own_post:
                                record.comments = [a for a in record.comments if a.content_object.content_object.author == u]
                                record['own_comments_only'] = True
                            else:
                                del record['comments']

                        if not u.subscription_settings.notify_accepted:
                            del record['accepted']

                        if record.get('answers', False) or record.get('comments', False) or record.get('accepted', False):
                            activity_in_subscriptions.append({'question': r.question, 'activity': record})
                    except:
                        pass

                context['activity_in_subscriptions'] = activity_in_subscriptions
            else:
                context['activity_in_subscriptions'] = False


            if u.subscription_settings.new_question == char_in_db:
                context['new_questions'] = new_questions
                context['watched_tags_only'] = False
            elif u.subscription_settings.new_question_watched_tags == char_in_db:
                context['new_questions'] = [q for q in new_questions if
                                            q.tags.filter(id__in=u.marked_tags.filter(user_selections__reason='good')).count() > 0]
                context['watched_tags_only'] = True
            else:
                context['new_questions'] = False

            if context['new_users'] or context['activity_in_subscriptions'] or context['new_questions']:
                send_email(digest_subject, (u.username, u.email), "notifications/digest.html", context, threaded=False)


    def get_digest_control(self):
        try:
            digest_control = KeyValue.objects.get(key='DIGEST_CONTROL')
        except:
            digest_control = KeyValue(key='DIGEST_CONTROL', value={
                'LAST_DAILY': datetime.now() - timedelta(days=1),
                'LAST_WEEKLY': datetime.now() - timedelta(days=1),
            })

        return digest_control

    def prepare_activity(self, since):
        all_activity = Activity.objects.filter(active_at__gt=since, activity_type__in=(
            const.TYPE_ACTIVITY_ASK_QUESTION, const.TYPE_ACTIVITY_ANSWER,
            const.TYPE_ACTIVITY_COMMENT_QUESTION, const.TYPE_ACTIVITY_COMMENT_ANSWER,
            const.TYPE_ACTIVITY_MARK_ANSWER
        )).order_by('active_at')

        question_records = {}
        new_questions = []


        for activity in all_activity:
            try:
                question = self.get_question_for_activity(activity)

                if not question.id in question_records:
                    question_records[question.id] = QuestionRecord(question)

                question_records[question.id].log_activity(activity)

                if activity.activity_type == const.TYPE_ACTIVITY_ASK_QUESTION:
                    new_questions.append(question)
            except:
                pass

        return new_questions, question_records

    def get_question_for_activity(self, activity):
        if activity.activity_type == const.TYPE_ACTIVITY_ASK_QUESTION:
            question = activity.content_object
        elif activity.activity_type == const.TYPE_ACTIVITY_ANSWER:
            question = activity.content_object.question
        elif activity.activity_type == const.TYPE_ACTIVITY_COMMENT_QUESTION:
            question = activity.content_object.content_object
        elif activity.activity_type == const.TYPE_ACTIVITY_COMMENT_ANSWER:
            question = activity.content_object.content_object.question
        elif activity.activity_type == const.TYPE_ACTIVITY_MARK_ANSWER:
            question = activity.content_object.question
        else:
            raise Exception

        return question
