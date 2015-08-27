# coding: utf-8
# http://stackoverflow.com/questions/7878028/override-default-django-translations
_ = lambda s: s
django_standard_messages_to_override = [
_("Please enter a correct %(username)s and password. Note that both fields "
"may be case-sensitive."),
_("%(model_name)s with this %(field_label)s already exists."),
_("Enter a valid username."),
]