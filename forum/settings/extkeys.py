from base import Setting, SettingSet
from django.utils.translation import ugettext_lazy as _

EXT_KEYS_SET = SettingSet('extkeys', _('External Keys'), _("Keys for various external providers that your application may optionally use."), 100)

GOOGLE_SITEMAP_CODE = Setting('GOOGLE_SITEMAP_CODE', '', EXT_KEYS_SET, dict(
label = _("Google sitemap code"),
help_text = _("This is the code you get when you register your site at <a href='https://www.google.com/webmasters/tools/'>Google webmaster central</a>."),
required=False))

GOOGLE_ANALYTICS_KEY = Setting('GOOGLE_ANALYTICS_KEY', '', EXT_KEYS_SET, dict(                     
label = _("Google analytics key"),
help_text = _("Your Google analytics key. You can get one at the <a href='http://www.google.com/analytics/'>Google analytics official website</a>"),
required=False))

WORDPRESS_API_KEY = Setting('WORDPRESS_API_KEY', '', EXT_KEYS_SET, dict(
label = _("Wordpress API key"),
help_text = _("Your Wordpress API key. You can get one at <a href='http://wordpress.com/'>http://wordpress.com/</a>"),
required=False))

WORDPRESS_BLOG_URL = Setting('WORDPRESS_BLOG_URL', '', EXT_KEYS_SET, dict(
label = _("Wordpress blog url"),
help_text = _("Your Wordpress blog url. You can get one at <a href='http://wordpress.com/'>http://wordpress.com/</a>"),
required=False))




