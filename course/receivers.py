# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang, Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.dispatch import receiver

from accounts.models import User
from course.models import (
        Course, Participation, participation_status,
        ParticipationPreapproval,
        Event, ParticipationRole
        )

if False:
    from typing import List, Union, Text, Optional, Tuple, Any  # noqa


# {{{ Update enrollment status when a User/Course instance is saved

@receiver(post_save, sender=User)
@receiver(post_save, sender=Course)
@transaction.atomic
def update_requested_participation_status(sender, created, instance,
        **kwargs):
    # type: (Any, bool, Union[Course, User], **Any) -> None

    if created:
        return

    if isinstance(instance, Course):
        course = instance
        requested_qset = Participation.objects.filter(
                course=course, status=participation_status.requested)
    elif isinstance(instance, User):
        user = instance
        requested_qset = Participation.objects.filter(
                user=user, status=participation_status.requested)
    else:
        return

    if requested_qset:

        for requested in requested_qset:
            if isinstance(instance, Course):
                user = requested.user
            elif isinstance(instance, User):
                course = requested.course
            else:
                continue

            may_preapprove, roles = may_preapprove_role(course, user)

            if may_preapprove:
                from course.enrollment import handle_enrollment_request

                handle_enrollment_request(
                    course, user, participation_status.active, roles)


def may_preapprove_role(course, user):
    # type: (Course, User) -> Tuple[bool, Optional[List[Text]]]

    if not user.is_active:
        return False, None

    preapproval = None
    if user.email:
        try:
            preapproval = ParticipationPreapproval.objects.get(
                    course=course, email__iexact=user.email)
        except ParticipationPreapproval.DoesNotExist:
            if user.institutional_id:
                if not (course.preapproval_require_verified_inst_id
                        and not user.institutional_id_verified):
                    try:
                        preapproval = ParticipationPreapproval.objects.get(
                                    course=course,
                                    institutional_id__iexact=user.institutional_id)
                    except ParticipationPreapproval.DoesNotExist:
                        pass

    if preapproval:
        return True, list(preapproval.roles.all())
    else:
        return False, None

# }}}


# {{{ Flush redis cache on event save or delete

@receiver(post_delete, sender=Event)
def event_post_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None

    event = kwargs['instance']
    if event is not None:
        flush_event_cache(event.course)


@receiver(post_save, sender=Event)
def event_post_save_handler(sender, created, instance, **kwargs):
    # type: (Any, bool, Event, **Any) -> None

    flush_event_cache(instance.course)


def flush_event_cache(course):
    # type: (Course) -> None

    from django.core.exceptions import ImproperlyConfigured
    try:
        import django.core.cache as cache
    except ImproperlyConfigured:
        return

    def_cache = cache.caches["default"]
    if not hasattr(def_cache, "delete_pattern"):
        return

    from course.constants import DATESPECT_CACHE_KEY_PATTERN
    cache_pattern = DATESPECT_CACHE_KEY_PATTERN % {
        "course": course.identifier,
        "key": "*"
    }
    try:
        def_cache.delete_pattern(cache_pattern)
    except Exception as e:
        if isinstance(e, AttributeError):
            raise ImproperlyConfigured(
                "django-redis is not installed or properly configured. "
                "'default' cache must be using django-redis cache for "
                "Event cache.")
        raise
    return
# }}}


# {{{ remove role identifier cache if the participation or ParticipationRole
#  is updated.

@receiver(post_delete, sender=ParticipationRole)
@receiver(post_delete, sender=Participation)
def participation_and_role_post_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None

    obj = kwargs['instance']
    if isinstance(obj, ParticipationRole):
        participation = None
        course = obj.course
    else:
        participation = obj
        course = obj.course

    clear_participation_role_identifier_cache(course, participation)


@receiver(post_save, sender=ParticipationRole)
@receiver(post_save, sender=Participation)
def participation_and_role_post_save_handler(sender, created, instance, **kwargs):
    # type: (Any, bool, Union[ParticipationRole, Participation], **Any) -> None

    if created:
        if isinstance(instance, Participation):
            return

    if isinstance(instance, ParticipationRole):
        course = instance.course
        participation = None
    else:
        course = instance.course
        participation = instance

    clear_participation_role_identifier_cache(course, participation)


def clear_participation_role_identifier_cache(course, participation):
    # type: (Course, Optional[Participation]) -> None

    from django.core.exceptions import ImproperlyConfigured
    try:
        import django.core.cache as cache
    except ImproperlyConfigured:
        return

    def_cache = cache.caches["default"]

    from course.enrollment import get_participation_role_identifiers_cache_key
    cache_key = get_participation_role_identifiers_cache_key(course, participation)
    def_cache.delete(cache_key)
    return

# }}}
# vim: foldmethod=marker
