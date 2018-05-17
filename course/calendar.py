# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2014 Andreas Kloeckner"

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

import six
from six.moves import range
from json import dumps

from django.template.loader import render_to_string
from django.utils.translation import (
        ugettext_lazy as _, pgettext_lazy)
from django.contrib.auth.decorators import login_required
from course.utils import course_view, render_course_page
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.contrib import messages  # noqa
from django.urls import reverse
from django.http import JsonResponse
import django.forms as forms

from crispy_forms.layout import (  # noqa
    Layout, Div, ButtonHolder, Button, Submit, HTML, Field)

import datetime
from bootstrap3_datetime.widgets import DateTimePicker

from relate.utils import StyledForm, as_local_time, string_concat, StyledModelForm
from course.constants import (
        participation_permission as pperm,
        )
from course.models import Event
from django.shortcuts import get_object_or_404


class ModalStyledFormMixin(object):
    ajax_modal_form_template = "modal-form.html"

    @property
    def form_description(self):
        raise NotImplementedError()

    @property
    def modal_id(self):
        raise NotImplementedError()

    def get_ajax_form_helper(self):
        return self.get_form_helper()

    def render_ajax_modal_form_html(self, request, context=None):
        self.helper.inputs = []

        from crispy_forms.utils import render_crispy_form
        from django.template.context_processors import csrf
        helper = self.get_ajax_form_helper()
        helper.template = self.ajax_modal_form_template
        if context is None:
            context = {}
        context.update(csrf(request))
        return render_crispy_form(self, helper, context)

# {{{ creation

class RecurringEventForm(ModalStyledFormMixin, StyledForm):

    form_description = _("Create recurring events")
    modal_id = "create-recurring-events-modal"

    # This is to avoid field name conflict
    prefix = "recurring"

    kind = forms.CharField(required=True,
            help_text=_("Should be lower_case_with_underscores, no spaces "
                        "allowed."),
            label=pgettext_lazy("Kind of event", "Kind of event"))
    time = forms.DateTimeField(
            widget=DateTimePicker(
                options={"format": "YYYY-MM-DD HH:mm", "sideBySide": True}),
            label=pgettext_lazy("Starting time of event", "Starting time"))
    duration_in_minutes = forms.FloatField(required=False,
            label=_("Duration in minutes"))
    all_day = forms.BooleanField(
                required=False,
                initial=False,
                label=_("All-day event"),
                help_text=_("Only affects the rendering in the class calendar, "
                "in that a start time is not shown"))
    shown_in_calendar = forms.BooleanField(
            required=False,
            initial=True,
            label=_('Shown in calendar'))
    interval = forms.ChoiceField(required=True,
            choices=(
                ("weekly", _("Weekly")),
                ("biweekly", _("Bi-Weekly")),
                ),
            label=pgettext_lazy("Interval of recurring events", "Interval"))
    starting_ordinal = forms.IntegerField(required=False,
            label=pgettext_lazy(
                "Starting ordinal of recurring events", "Starting ordinal"))
    count = forms.IntegerField(required=True,
            label=pgettext_lazy("Count of recurring events", "Count"))

    def __init__(self, course_identifier, *args, **kwargs):
        super(RecurringEventForm, self).__init__(*args, **kwargs)
        self.course_identifier = course_identifier

        self.helper.add_input(
                Submit("submit", _("Create")))

    def get_ajax_form_helper(self):
        helper = self.get_form_helper()
        self.helper.form_action = reverse(
            "relate-create_recurring_events", args=[self.course_identifier])

        helper.layout = Layout(
            Div(*self.fields, css_class="modal-body"),
            ButtonHolder(
                Submit("submit", _("Create"),
                       css_class="btn btn-md btn-success"),
                Button("cancel", _("Cancel"),
                       css_class="btn btn-md btn-default",
                       data_dismiss="modal"),
                css_class="modal-footer"))
        return helper


class EventAlreadyExists(Exception):
    pass


@transaction.atomic
def _create_recurring_events_backend(course, time, kind, starting_ordinal, interval,
        count, duration_in_minutes, all_day, shown_in_calendar):
    ordinal = starting_ordinal

    import datetime

    for i in range(count):
        evt = Event()
        evt.course = course
        evt.kind = kind
        evt.ordinal = ordinal
        evt.time = time
        evt.all_day = all_day
        evt.shown_in_calendar = shown_in_calendar

        if duration_in_minutes:
            evt.end_time = evt.time + datetime.timedelta(
                    minutes=duration_in_minutes)
        try:
            evt.save()
        except IntegrityError:
            raise EventAlreadyExists(
                        _("'%(exist_event)s' already exists.")
                        % {'exist_event': evt})

        date = time.date()
        if interval == "weekly":
            date += datetime.timedelta(weeks=1)
        elif interval == "biweekly":
            date += datetime.timedelta(weeks=2)
        else:
            raise NotImplementedError()

        time = time.tzinfo.localize(
                datetime.datetime(date.year, date.month, date.day,
                    time.hour, time.minute, time.second))
        del date

        ordinal += 1


@login_required
@course_view
def create_recurring_events(pctx):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    message = None
    message_level = None

    if request.method == "GET" and request.is_ajax():
        raise PermissionDenied(_("may not GET by AJAX"))

    if request.method == "POST":
        form = RecurringEventForm(
            pctx.course.identifier, request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data["starting_ordinal"] is not None:
                starting_ordinal = form.cleaned_data["starting_ordinal"]
                starting_ordinal_specified = True
            else:
                starting_ordinal = 1
                starting_ordinal_specified = False

            while True:
                try:
                    _create_recurring_events_backend(
                            course=pctx.course,
                            time=form.cleaned_data["time"],
                            kind=form.cleaned_data["kind"],
                            starting_ordinal=starting_ordinal,
                            interval=form.cleaned_data["interval"],
                            count=form.cleaned_data["count"],
                            duration_in_minutes=(
                                form.cleaned_data["duration_in_minutes"]),
                            all_day=form.cleaned_data["all_day"],
                            shown_in_calendar=(
                                form.cleaned_data["shown_in_calendar"])
                            )
                except EventAlreadyExists as e:
                    if starting_ordinal_specified:
                        message = (
                                string_concat(
                                    "%(err_type)s: %(err_str)s. ",
                                    _("No events created."))
                                % {
                                    "err_type": type(e).__name__,
                                    "err_str": str(e)})
                        message_level = messages.ERROR
                    else:
                        starting_ordinal += 10
                        continue

                except Exception as e:
                    message = (
                            string_concat(
                                "%(err_type)s: %(err_str)s. ",
                                _("No events created."))
                            % {
                                "err_type": type(e).__name__,
                                "err_str": str(e)})
                    message_level = messages.ERROR
                else:
                    message = _("Events created.")

                break
        else:
            if request.is_ajax():
                return JsonResponse(form.errors, status=400)

        if request.is_ajax():
            if message_level == messages.ERROR:
                # Rendered as a non-field error in AJAX view
                return JsonResponse({"__all__": [message]}, status=400)
            return JsonResponse({"message": message})

    form = RecurringEventForm(pctx.course.identifier)

    if message and message_level:
        messages.add_message(request, message_level, message)
    return render_course_page(pctx, "course/generic-course-form.html", {
        "form": form,
        "form_description": _("Create recurring events"),
    })


class RenumberEventsForm(ModalStyledFormMixin, StyledForm):
    form_description = _("Renumber events")
    modal_id = "renumber-events-modal"

    # This is to avoid field name conflict
    prefix = "renumber"

    kind = forms.CharField(required=True,
            help_text=_("Should be lower_case_with_underscores, no spaces "
                        "allowed."),
            label=pgettext_lazy("Kind of event", "Kind of event"))
    starting_ordinal = forms.IntegerField(required=True, initial=1,
            label=pgettext_lazy(
                "Starting ordinal of recurring events", "Starting ordinal"))

    def __init__(self, course_identifier, *args, **kwargs):
        super(RenumberEventsForm, self).__init__(*args, **kwargs)
        self.course_identifier = course_identifier

        self.helper.add_input(
                Submit("submit", _("Renumber")))

    def get_ajax_form_helper(self):
        helper = self.get_form_helper()
        self.helper.form_action = reverse(
            "relate-renumber_events", args=[self.course_identifier])

        helper.layout = Layout(
            Div(*self.fields, css_class="modal-body"),
            ButtonHolder(
                Submit("submit", _("Renumber"),
                       css_class="btn btn-md btn-success"),
                Button("cancel", _("Cancel"),
                       css_class="btn btn-md btn-default",
                       data_dismiss="modal"),
                css_class="modal-footer"))
        return helper


@transaction.atomic
@login_required
@course_view
def renumber_events(pctx):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request

    if request.method == "GET" and request.is_ajax():
        raise PermissionDenied(_("may not GET by AJAX"))

    message = None
    message_level = None

    if request.method == "POST":
        form = RenumberEventsForm(
            pctx.course.identifier, request.POST, request.FILES)
        if form.is_valid():
            events = list(Event.objects
                    .filter(course=pctx.course, kind=form.cleaned_data["kind"])
                    .order_by('time'))

            if events:
                queryset = (Event.objects
                    .filter(course=pctx.course, kind=form.cleaned_data["kind"]))

                queryset.delete()

                ordinal = form.cleaned_data["starting_ordinal"]
                for event in events:
                    new_event = Event()
                    new_event.course = pctx.course
                    new_event.kind = form.cleaned_data["kind"]
                    new_event.ordinal = ordinal
                    new_event.time = event.time
                    new_event.end_time = event.end_time
                    new_event.all_day = event.all_day
                    new_event.shown_in_calendar = event.shown_in_calendar
                    new_event.save()

                    ordinal += 1

                message = _("Events renumbered.")
                message_level = messages.SUCCESS
            else:
                message = _("No events found.")
                message_level = messages.SUCCESS
                messages.add_message(request, messages.ERROR,
                        _("No events found."))
        else:
            if request.is_ajax():
                return JsonResponse(form.errors, status=400)

        if request.is_ajax():
            if message_level == messages.ERROR:
                # Rendered as a non-field error in AJAX view
                return JsonResponse({"__all__": [message]}, status=400)
            return JsonResponse({"message": message})

    else:
        form = RenumberEventsForm(pctx.course.identifier)

    if messages and message_level:
        messages.add_message(request, message_level, message)
    return render_course_page(pctx, "course/generic-course-form.html", {
        "form": form,
        "form_description": _("Renumber events"),
    })

# }}}


# {{{ calendar

class EventInfo(object):
    def __init__(self, id, human_title, start_time, end_time, description, show_description):
        self.id = id
        self.human_title = human_title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.show_description = show_description


def get_event_json(pctx, now_datetime=None, is_edit_view=False):
    events_json = []

    from course.content import (
        get_raw_yaml_from_repo, markup_to_html, parse_date_spec)
    try:
        event_descr = get_raw_yaml_from_repo(pctx.repo,
                                             pctx.course.events_file,
                                             pctx.course_commit_sha)
    except ObjectDoesNotExist:
        event_descr = {}

    if not now_datetime:
        from course.views import get_now_or_fake_time
        now_datetime = get_now_or_fake_time(pctx.request)

    event_kinds_desc = event_descr.get("event_kinds", {})
    event_info_desc = event_descr.get("events", {})
    events_info = []

    may_edit_events = pctx.has_permission(pperm.edit_events)

    filter_kwargs = {"course": pctx.course}
    if not may_edit_events:
        # exclude hidden events when no edit permission
        filter_kwargs["shown_in_calendar"] = True

    events = sorted(
        Event.objects.filter(**filter_kwargs),
        key=lambda evt: (
            -evt.time.year, -evt.time.month, -evt.time.day,
            evt.time.hour, evt.time.minute, evt.time.second))

    for event in events:
        kind_desc = event_kinds_desc.get(event.kind)

        human_title = six.text_type(event)

        event_json = {
            "id": event.id,
            "start": event.time.isoformat(),
            "allDay": event.all_day}

        if event.end_time is not None:
            event_json["end"] = event.end_time.isoformat()

        if kind_desc is not None:
            if "color" in kind_desc:
                event_json["color"] = kind_desc["color"]
            if "title" in kind_desc:
                if event.ordinal is not None:
                    human_title = kind_desc["title"].format(nr=event.ordinal)
                else:
                    human_title = kind_desc["title"].rstrip("{nr}").strip()

        if may_edit_events:
            event_json["shown_in_calendar"] = event.shown_in_calendar
            event_json["delete_form_url"] = reverse(
                "relate-get_delete_event_form",
                args=[pctx.course.identifier, event.id])
            event_json["update_form_url"] = reverse(
                "relate-get_update_event_form",
                args=[pctx.course.identifier, event.id])
            event_json["str"] = str(event)

        description = None
        show_description = True and event.shown_in_calendar
        event_desc = event_info_desc.get(six.text_type(event))
        if event_desc is not None:
            if "description" in event_desc:
                description = markup_to_html(
                    pctx.course, pctx.repo, pctx.course_commit_sha,
                    event_desc["description"])

            if "title" in event_desc:
                human_title = event_desc["title"]

            if "color" in event_desc:
                event_json["color"] = event_desc["color"]

            if "show_description_from" in event_desc:
                ds = parse_date_spec(
                    pctx.course, event_desc["show_description_from"])
                if now_datetime < ds:
                    show_description = False

            if "show_description_until" in event_desc:
                ds = parse_date_spec(
                    pctx.course, event_desc["show_description_until"])
                if now_datetime > ds:
                    show_description = False

        event_json["title"] = human_title
        if may_edit_events:
            event_json['show_description'] = show_description

        if description and (show_description or may_edit_events):
            # Fixme: participation with pperm.edit_events will
            # always see the url (both edit view and normal view)
            event_json["url"] = "#event-%d" % event.id

            start_time = event.time
            end_time = event.end_time

            if event.all_day:
                start_time = start_time.date()
                if end_time is not None:
                    local_end_time = as_local_time(end_time)
                    end_midnight = datetime.time(tzinfo=local_end_time.tzinfo)
                    if local_end_time.time() == end_midnight:
                        end_time = (end_time - datetime.timedelta(days=1)).date()
                    else:
                        end_time = end_time.date()

            events_info.append(
                EventInfo(
                    id=event.id,
                    human_title=human_title,
                    start_time=start_time,
                    end_time=end_time,
                    description=description,
                    show_description=show_description
                ))

        events_json.append(event_json)

    from django.template.loader import render_to_string
    events_info_html = render_to_string(
        "course/events_info.html",
        context={"events_info": events_info,
                 "may_edit_events": may_edit_events,
                 "is_edit_view": is_edit_view},
        request=pctx.request)

    return events_info_html, events_json


@course_view
def view_calendar(pctx, operation=None):
    if not pctx.has_permission(pperm.view_calendar):
        raise PermissionDenied(_("may not view calendar"))

    is_edit_view = bool(operation == "edit")
    may_edit_calendar = pctx.has_permission(pperm.edit_events)
    if is_edit_view and not may_edit_calendar:
        raise PermissionDenied(_("may not edit calendar"))

    from course.views import get_now_or_fake_time
    now = get_now_or_fake_time(pctx.request)

    default_date = now.date()
    if pctx.course.end_date is not None and default_date > pctx.course.end_date:
        default_date = pctx.course.end_date

    new_event_form = CreateEventModalForm(pctx.course.identifier)
    new_event_form_ajax_html = (
        new_event_form.render_ajax_modal_form_html(pctx.request))

    recurring_events_form = RecurringEventForm(pctx.course.identifier)
    recurring_events_form_ajax_html = (
        recurring_events_form.render_ajax_modal_form_html(pctx.request))

    renumber_events_form = RenumberEventsForm(pctx.course.identifier)
    renumber_events_form_ajax_html = (
        renumber_events_form.render_ajax_modal_form_html(pctx.request))

    return render_course_page(pctx, "course/calendar.html", {
        "default_date": default_date.isoformat(),
        "is_edit_mode": is_edit_view,
        "new_event_form": new_event_form,
        "new_event_form_ajax_html": new_event_form_ajax_html,

        "recurring_events_form": RecurringEventForm(pctx.course.identifier),
        "recurring_events_form_ajax_html": recurring_events_form_ajax_html,

        "renumber_events_form": renumber_events_form,
        "renumber_events_form_ajax_html": renumber_events_form_ajax_html,

        # Wrappers used by JavaScript template (tmpl) so as not to
        # conflict with Django template's tag wrapper
        "JQ_OPEN": '{%',
        'JQ_CLOSE': '%}',
    })


@course_view
def fetch_event_json(pctx, is_edit_view):
    if not pctx.has_permission(pperm.view_calendar):
        raise PermissionDenied(_("may not view calendar"))

    events_info_html, events_json = get_event_json(
        pctx, now_datetime=None, is_edit_view=bool(int(is_edit_view)))

    return JsonResponse(
        {"events_json": events_json,
         "events_info_html": events_info_html},
        safe=False)


class CreateEventModalForm(ModalStyledFormMixin, StyledModelForm):
    form_description = _("Create a event")
    modal_id = "create-event-modal"
    prefix = "create"

    class Meta:
        model = Event
        fields = ['kind', 'ordinal', 'time',
                  'end_time', 'all_day', 'shown_in_calendar']
        widgets = {
            "time": DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
            "end_time": DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
        }

    def __init__(self, course_identifier, *args, **kwargs):
        super(CreateEventModalForm, self).__init__(*args, **kwargs)
        self.fields["shown_in_calendar"].help_text = (
            _("Shown in students' calendar"))

        self.course_identifier = course_identifier

    def get_ajax_form_helper(self):
        helper = self.get_form_helper()

        self.helper.form_action = reverse(
            "relate-create_event", args=[self.course_identifier])

        helper.layout = Layout(
            Div(*self.fields, css_class="modal-body"),
            ButtonHolder(
                Submit("save", _("Save"),
                       css_class="btn btn-md btn-success"),
                Button("cancel", _("Cancel"),
                       css_class="btn btn-md btn-default",
                       data_dismiss="modal"),
                css_class="modal-footer"
            )
        )
        return helper

    def clean(self):
        kind = self.cleaned_data.get("kind")
        ordinal = self.cleaned_data.get('ordinal')
        if kind is not None:
            filter_kwargs = {"course__identifier": self.course_identifier,
                             "kind": kind}
            if ordinal is not None:
                filter_kwargs["ordinal"] = ordinal
            else:
                filter_kwargs["ordinal__isnull"] = True

            qset = Event.objects.filter(**filter_kwargs)
            if qset.count():
                from django.forms import ValidationError
                raise ValidationError(
                        _("'%(exist_event)s' already exists.")
                        % {'exist_event': qset[0]})


@course_view
@transaction.atomic()
def create_event(pctx):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    if not request.is_ajax() or request.method != "POST":
        raise PermissionDenied(_("only AJAX POST is allowed"))

    form = CreateEventModalForm(
        pctx.course.identifier, request.POST, request.FILES)

    if form.is_valid():
        try:
            instance = form.save(commit=False)
            instance.course = pctx.course
            instance.save()

            message = (_("Event created: '%s'.") % str(instance))
            return JsonResponse({"message": message})
        except Exception as e:
            return JsonResponse(
                {"__all__": ["%s: %s" % type(e).__name__, str(e)]}, status=400)
    else:
        return JsonResponse(form.errors, status=400)


class DeleteEventForm(ModalStyledFormMixin, StyledModelForm):
    form_description = _("Delete event")
    modal_id = "delete-event-modal"
    prefix = "delete"

    class Meta:
        model = Event
        fields = []

    def __init__(self, course_identifier, instance_to_delete, *args, **kwargs):
        super(DeleteEventForm, self).__init__(*args, **kwargs)

        self.course_identifier = course_identifier

        hint = _("Are you sure to delete event '%s'?") % str(instance_to_delete)

        if instance_to_delete.ordinal is not None:
            events_of_same_kind = Event.objects.filter(
                    course__identifier=course_identifier,
                    kind=instance_to_delete.kind, ordinal__isnull=False)
            if events_of_same_kind.count() > 1:
                choices = [
                    ("delete_single",
                     _("Delete event '%s'") % str(instance_to_delete)),
                    ('delete_all',
                     _("Delete all events with "
                       "kind '%s'") % instance_to_delete.kind),
                ]

                if events_of_same_kind.filter(
                        time__gt=instance_to_delete.time).count():
                    choices.append(
                        ('delete_following',
                         _("Delete this and following events with "
                           "kind '%s'") % instance_to_delete.kind),
                    )

                week_day = instance_to_delete.time.weekday()
                hour = instance_to_delete.time.hour
                minute = instance_to_delete.time.minute

                events_of_same_kind_and_weekday_time = (
                    Event.objects.filter(
                        course__identifier=course_identifier,
                        # kind=instance_to_delete.kind,
                        time__hour=hour,
                    # events_of_same_kind.filter(
                    #     # time__week_day=week_day,
                    #     time__hour=hour,
                    #     # time__minute=minute
                    ))

                print(events_of_same_kind_and_weekday_time.count(), "here!!!")
                print(Event.objects.filter(time__hour=hour).count())

                if (events_of_same_kind.count() > events_of_same_kind_and_weekday_time.count() > 1):

                    from relate.utils import format_datetime_local

                    choices.append(
                        ("delete_all_of_same_series",
                         _("Delete this and following events with "
                           "kind '%(kind)s' at '%(time)s'")
                         % {"kind": instance_to_delete.kind,
                            "time": format_datetime_local(
                                instance_to_delete.time, format="D, HH:mm")}),
                    )

                self.fields["operation"] = (
                    forms.ChoiceField(
                        choices=choices, widget=forms.RadioSelect(), required=True,
                        initial="delete_single",
                        label=_("Operation")))
                hint = _("Select your operation:")

        self.instance_to_delete = instance_to_delete
        self.hint = hint

    def get_ajax_form_helper(self):
        helper = super(DeleteEventForm, self).get_ajax_form_helper()

        self.helper.form_action = reverse(
            "relate-delete_event", args=[
                self.course_identifier, self.instance_to_delete.pk])

        helper.layout = Layout(
            Div(*self.fields, css_class="modal-body"),
            ButtonHolder(
                Submit("submit", _("Delete"),
                       css_class="btn btn-md btn-danger"),
                Button("cancel", _("Cancel"),
                       css_class="btn btn-md btn-default",
                       data_dismiss="modal"),
                css_class="modal-footer"))
        helper.layout[0].insert(0, HTML(self.hint))
        return helper


@course_view
def get_delete_event_form(pctx, event_id):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    if not (request.is_ajax() and request.method == "GET"):
        raise PermissionDenied(_("only AJAX GET is allowed"))

    event_id = int(event_id)
    instance_to_delete = get_object_or_404(Event, course=pctx.course, id=event_id)

    form = DeleteEventForm(
        pctx.course.identifier, instance_to_delete, instance=instance_to_delete)

    return JsonResponse(
        {"form_html": form.render_ajax_modal_form_html(pctx.request)})


@course_view
@transaction.atomic()
def delete_event(pctx, event_id):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    if not request.is_ajax() or request.method != "POST":
        raise PermissionDenied(_("only AJAX POST is allowed"))

    event_id = int(event_id)
    event_qs = Event.objects.filter(course=pctx.course, pk=event_id)
    if not event_qs.count():
        from django.http import Http404
        raise Http404()
    else:
        instance_to_delete, = event_qs
        form = DeleteEventForm(
            pctx.course.identifier, instance_to_delete,
            request.POST, instance=instance_to_delete)

        if form.is_valid():
            operation = form.cleaned_data.get("operation")
            if operation is None or operation == "delete_single":
                qset = event_qs
                message = _("Event '%s' deleted.") % str(instance_to_delete)
            elif operation in "delete_following":
                qset = Event.objects.filter(
                    course=pctx.course, kind=instance_to_delete.kind,
                    time__gte=instance_to_delete.time)
                message = _("%(number)d events of kind '%(kind)s' deleted."
                            ) % {"number": qset.count(),
                                 "kind": instance_to_delete.kind}
            elif operation == "delete_all":
                qset = Event.objects.filter(
                    course=pctx.course, kind=instance_to_delete.kind, ordinal__isnull=False)
                message = _("All events of kind '%(kind)s' deleted."
                            ) % {"kind": instance_to_delete.kind}
            else:
                raise NotImplementedError()

            try:
                qset.delete()
                return JsonResponse({"message": message})
            except Exception as e:
                return JsonResponse(
                    {"__all__": ["%s: %s" % (type(e).__name__, str(e))]},
                    status=400)

        else:
            return JsonResponse(form.errors, status=400)


class UpdateEventForm(ModalStyledFormMixin, StyledModelForm):
    @property
    def form_description(self):
        return _("Update event")
    modal_id = "update-event-modal"
    prefix = "update"

    class Meta:
        model = Event
        fields = ['kind', 'ordinal', 'time',
                  'end_time', 'all_day', 'shown_in_calendar']
        widgets = {
            "time": DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
            "end_time": DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}),
        }

    def __init__(self, course_identifier, event_id, *args, **kwargs):
        super(UpdateEventForm, self).__init__(*args, **kwargs)

        self.course_identifier = course_identifier
        self.event_id = event_id

    def get_ajax_form_helper(self):
        helper = super(UpdateEventForm, self).get_ajax_form_helper()
        self.helper.form_action = reverse(
            "relate-update_event", args=[self.course_identifier, self.event_id])

        helper.layout = Layout(
            Div(*self.fields, css_class="modal-body"),
            ButtonHolder(
                Submit("submit", _("Update"),
                       css_class="btn btn-md btn-success"),
                Button("cancel", _("Cancel"),
                       css_class="btn btn-md btn-default",
                       data_dismiss="modal"),
                css_class="modal-footer"))
        return helper

    def clean(self):
        kind = self.cleaned_data.get("kind")
        ordinal = self.cleaned_data.get('ordinal')

        if kind is not None:
            filter_kwargs = {"course__identifier": self.course_identifier,
                             "kind": kind}
            if ordinal is not None:
                filter_kwargs["ordinal"] = ordinal
            else:
                filter_kwargs["ordinal__isnull"] = True

            qset = Event.objects.filter(**filter_kwargs)
            if qset.exists():
                assert qset.count() == 1
                exist_event, = qset
                if exist_event.pk != self.event_id:
                    from django.forms import ValidationError
                    raise ValidationError(
                        _("'%(exist_event)s' already exists.")
                        % {'exist_event': exist_event})


@course_view
def get_update_event_form(pctx, event_id):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    if not (request.is_ajax() and request.method == "GET"):
        raise PermissionDenied(_("only AJAX GET is allowed"))

    event_id = int(event_id)
    instance = get_object_or_404(Event, course=pctx.course, id=event_id)

    form = UpdateEventForm(
        pctx.course.identifier, event_id, instance=instance)

    return JsonResponse(
        {"form_html": form.render_ajax_modal_form_html(pctx.request)})


@course_view
@transaction.atomic()
def update_event(pctx, event_id):
    if not pctx.has_permission(pperm.edit_events):
        raise PermissionDenied(_("may not edit events"))

    request = pctx.request
    if not request.is_ajax() or request.method != "POST":
        raise PermissionDenied(_("only AJAX POST is allowed"))

    event_id = int(event_id)
    get_object_or_404(Event, course=pctx.course, id=event_id)

    form = UpdateEventForm(
        pctx.course.identifier, event_id, request.POST, request.FILES)

    if form.is_valid():
        try:
            instance = form.save(commit=False)
            instance.course = pctx.course
            instance.pk = event_id
            instance.save()

            message = _("Event '%s' updated.") % str(instance)
            return JsonResponse({"message": message})
        except Exception as e:
            return JsonResponse(
                {"__all__": ["%s: %s" % type(e).__name__, str(e)]}, status=400)
    else:
        return JsonResponse(form.errors, status=400)

# vim: foldmethod=marker
