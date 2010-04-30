from base import Setting, SettingSet
from django.forms.widgets import Textarea

FAQ_SET = SettingSet('faq', 'FAQ page', "Define the text in the about page. You can use markdown and some basic html tags.", 2000, True)

FAQ_PAGE_TEXT = Setting('FAQ_PAGE_TEXT',
"""
**Please customize this text in the administration area**

**Frequently Asked Questions (FAQ)**

**What kinds of questions can I ask here?**

Most importantly - questions should be relevant to this community. Before you ask - please make sure to search for a similar question. You can search questions by their title or tags.

**What kinds of questions should be avoided?**

Please avoid asking questions that are not relevant to this community, too subjective and argumentative.

**What should I avoid in my answers?**

OSQA: Open Source Q&A Forum is a question and answer site - it is not a discussion group. Please avoid holding debates in your answers as they tend to dilute the essense of questions and answers. For the brief discussions please use commenting facility.

**Who moderates this community?**

The short answer is: you. This website is moderated by the users. Karma system allows users to earn rights to perform a variety of moderation tasks

**How does karma system work?**

When a question or answer is upvoted, the user who posted them will gain some points, which are called "karma points". These points serve as a rough measure of the community trust to him/her. Various moderation tasks are gradually assigned to the users based on those points.

For example, if you ask an interesting question or give a helpful answer, your input will be upvoted. On the other hand if the answer is misleading - it will be downvoted. Each vote in favor will generate 10 points, each vote against will subtract 2 points. There is a limit of 200 points that can be accumulated per question or answer. The table below explains reputation point requirements for each type of moderation task.

* add comments
* downvote
* close own questions
* reopen own questions
* retag questions
* edit any answer
* open any closed question
* delete any comment

**What is gravatar?**

Gravatar means globally recognized avatar - your unique avatar image associated with your email address. It's simply a picture that shows next to your posts on the websites that support gravatar protocol. By default gravar appears as a square filled with a snowflake-like figure. You can set your image at gravatar.com

**To register, do I need to create new password?**

No, you don't have to. You can login through any service that supports OpenID, e.g. Google, Yahoo, AOL, etc. Login now!

**Why other people can edit my questions/answers?**

Goal of this site is... So questions and answers can be edited like wiki pages by experienced users of this site and this improves the overall quality of the knowledge base content. If this approach is not for you, we respect your choice.

**Still have questions?**

Please ask your question, help make our community better!
""", FAQ_SET, dict(
label = "FAQ page text",
help_text = " The faq page. ",
widget=Textarea(attrs={'rows': '25'})))