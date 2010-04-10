import os
from django import forms
from base import Setting, StringSetting, IntegerSetting, BoolSetting, FloatSetting
from django.utils.translation import ugettext as _
from django.core.files.storage import FileSystemStorage

class SettingsSetForm(forms.Form):
    def __init__(self, set, data=None, *args, **kwargs):
        if data is None:
            data = dict([(setting.name, setting.value) for setting in set])

        super(SettingsSetForm, self).__init__(data, *args, **kwargs)

        for setting in set:
            if isinstance(setting, StringSetting):
                field = forms.CharField(**setting.field_context)
            elif isinstance(setting, FloatSetting):
                field = forms.FloatField(**setting.field_context)
            elif isinstance(setting, IntegerSetting):
                field = forms.IntegerField(**setting.field_context)
            elif isinstance(setting, BoolSetting):
                field = forms.BooleanField(**setting.field_context)
            else:
                field = forms.CharField(**setting.field_context)

            self.fields[setting.name] = field

        self.set = set

    def save(self):
        for setting in self.set:
            setting.set_value(self.cleaned_data[setting.name])

class ImageFormWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return """
            <img src="%(value)s" /><br />
            %(change)s: <input type="file" name="%(name)s" />
            <input type="hidden" name="%(name)s_old" value="%(value)s" />
            """ % {'name': name, 'value': value, 'change': _('Change this:')}

    def value_from_datadict(self, data, files, name):
        if name in files:
            f = files[name]

            # check file type
            file_name_suffix = os.path.splitext(f.name)[1].lower()

            if not file_name_suffix in ('.jpg', '.jpeg', '.gif', '.png', '.bmp', '.tiff', '.ico'):
                raise Exception('File type not allowed')

            from forum.settings import UPFILES_FOLDER, UPFILES_ALIAS

            storage = FileSystemStorage(str(UPFILES_FOLDER), str(UPFILES_ALIAS))
            new_file_name = storage.save(f.name, f)
            return str(UPFILES_ALIAS) + new_file_name
        else:
            if "%s_old" % name in data:
                return data["%s_old" % name]
            elif name in data:
                return data[name]


