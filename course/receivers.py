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

from django.db.models.signals import post_save, post_delete, m2m_changed, pre_delete
from django.db import transaction
from django.dispatch import receiver

from accounts.models import User
from course.models import (
        Course, Participation, participation_status,
        ParticipationPreapproval, FlowSession, GradeChange,
        Event, ParticipationRole, ParticipationTag
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

    user_updated = False
    course_updated = False

    if isinstance(instance, Course):
        course_updated = True
        course = instance
        requested_qset = Participation.objects.filter(
                course=course, status=participation_status.requested)
    else:
        assert isinstance(instance, User)
        user_updated = True
        user = instance
        requested_qset = Participation.objects.filter(
                user=user, status=participation_status.requested)

    for requested in requested_qset:
        if course_updated:
            user = requested.user
        else:
            assert user_updated
            course = requested.course

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
            pass
    if preapproval is None:
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


# {{{ remove participationTags cache if the participationTag is updated.

@receiver(pre_delete, sender=ParticipationTag)
def participationtag_pre_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None
    instance = kwargs.get("instance", None)
    if not instance:
        return
    assert instance.pk

    # This is saved for post_delete of Ptags since afterward those
    # participations were not able to be filtered out as the tag
    # had been removed from the participation objects.
    instance._old_participation_set = set(
        list(
            Participation.objects.filter(
                course=instance.course, tags__pk=instance.pk)
            .prefetch_related("tags")))


@receiver(post_delete, sender=ParticipationTag)
def participationtag_post_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None
    ptag = kwargs['instance']
    for participation in ptag._old_participation_set:
        remove_participationtag_cache(ptag.pk, participation=participation)


@receiver(m2m_changed, sender=Participation.tags.through)
def participationtag_changed_handler(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    reverse = kwargs.pop("reverse")
    if isinstance(instance, Participation):
        if action in ["post_add", "post_remove"] and not reverse:
            changed_ptag_pk_list = list(
                ParticipationTag.objects.filter(pk__in=pk_set)
                .values_list("pk", flat=True))
            for pk in changed_ptag_pk_list:
                pass
                remove_participationtag_cache(pk, participation=instance)


@receiver(post_save, sender=ParticipationTag)
def participationtag_post_save_handler(sender, created, instance, **kwargs):
    # type: (Any, bool, ParticipationTag, **Any) -> None
    if created:
        return
    remove_participationtag_cache(instance.pk, course=instance.course)


def remove_participationtag_cache(tag_pk, participation=None, course=None):
    # type: (int, Optional[Participation], Optional[Course]) -> None

    from django.core.exceptions import ImproperlyConfigured
    try:
        import django.core.cache as cache
    except ImproperlyConfigured:
        return

    def_cache = cache.caches["default"]

    if participation:
        participations = [participation]
    else:
        if not course:
            return
        participations = list(Participation.objects
                      .filter(course=course, tags__pk=tag_pk)
                      .prefetch_related("tags"))

    from course.utils import get_participation_tag_cache_key
    cache_keys = [get_participation_tag_cache_key(participation)
                  for participation in participations]
    def_cache.delete_many(cache_keys)
    return

# }}}


# {{{ remove participationRole cache if the participationRole is updated.

@receiver(pre_delete, sender=ParticipationRole)
def participation_roles_pre_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None
    instance = kwargs.get("instance", None)
    if not instance:
        return
    assert instance.pk

    # This is saved for post_delete of Proles since afterward those
    # related participations were not able to be filtered out as the roles
    # had been removed from the participation objects.
    instance._old_participation_set = set(
        list(
            Participation.objects.filter(
                course=instance.course, roles__pk=instance.pk)
            .prefetch_related("tags")))


@receiver(post_delete, sender=ParticipationRole)
def participation_roles_post_delete_handler(sender, **kwargs):
    # type: (Any, **Any) -> None
    roles = kwargs['instance']
    for participation in roles._old_participation_set:
        remove_participation_roles_cache(
            roles.pk, roles.course, participation=participation
        )
    remove_participation_roles_cache(
        roles.pk, roles.course, for_unenrolled=True)


@receiver(m2m_changed, sender=Participation.roles.through)
def participation_roles_changed_handler(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    reverse = kwargs.pop("reverse")
    if isinstance(instance, Participation):
        if action in ["post_add", "post_remove"] and not reverse:
            changed_ptag_pk_list = list(
                ParticipationRole.objects.filter(pk__in=pk_set)
                .values_list("pk", flat=True))
            for pk in changed_ptag_pk_list:
                remove_participation_roles_cache(
                    pk, course=instance.course, participation=instance)


@receiver(post_save, sender=ParticipationRole)
def participation_roles_post_save_handler(sender, created, instance, **kwargs):
    # type: (Any, bool, ParticipationRole, **Any) -> None
    remove_participation_roles_cache(
        instance.pk, course=instance.course, for_unenrolled=True)


def remove_participation_roles_cache(
        roles_pk, course, participation=None, for_unenrolled=False):
    # type: (int, Course, Optional[Participation], Optional[bool]) -> None

    from django.core.exceptions import ImproperlyConfigured
    try:
        import django.core.cache as cache
    except ImproperlyConfigured:
        return

    def_cache = cache.caches["default"]

    if participation:
        participations = [participation]
    else:
        participations = list(Participation.objects
                      .filter(course=course, roles__pk=roles_pk)
                      .prefetch_related("roles"))

    if for_unenrolled:
        # Make sure when new ptags are created/deleted,
        # changed in admin, unenrolled/anonymous participation
        # get their roles updated too.
        participations.append(None)  # type: ignore

    from course.enrollment import get_participation_role_identifiers_cache_key
    cache_keys = [
        get_participation_role_identifiers_cache_key(
            course=course,
            participation=p)
        for p in participations]
    def_cache.delete_many(cache_keys)
    return


@receiver(post_delete, sender=FlowSession)
@transaction.atomic
def create_exempt_grade_change_when_delete_session(sender, instance, **kwargs):
    # type: (Any, FlowSession, **Any) -> None

    # FIXME: `exempt` is not designed to be used in ths way.
    """
    Create a :class:`GradeChange` entry with state "exempt" for the attempt_id
    of that flow_session, after deleting a flow session from admin. We are
    strongly against modifying data through admin, but this is helpful for
    debugging when developing.
    """
    from course.flow import get_flow_session_attempt_id
    last_gchanges = (
        GradeChange.objects
        # query using flow_session=instance will fail.
        .filter(attempt_id=get_flow_session_attempt_id(instance))
        .order_by("-grade_time")[:1])

    if not last_gchanges.count():
        return

    last_gchange, = last_gchanges

    from course.constants import grade_state_change_types

    last_gchange.pk = None
    last_gchange.points = None
    last_gchange.flow_session = None
    last_gchange.creator = None
    last_gchange.comment = None

    from django.utils.timezone import now
    last_gchange.grade_time = now()
    last_gchange.state = grade_state_change_types.exempt
    last_gchange.save()

# }}}
# vim: foldmethod=marker
