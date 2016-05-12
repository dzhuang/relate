from django.contrib import admin
from django.contrib.admin.options import IncorrectLookupParameters
from django.template.response import SimpleTemplateResponse
from django import forms
from django.utils.translation import (
    ugettext_lazy as _, string_concat, pgettext)
from django.utils.six.moves.urllib.parse import parse_qsl, urlparse, urlunparse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.core.urlresolvers import Resolver404, get_script_prefix, resolve, reverse
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponseRedirect

from course.admin import (
    admin_roles,
    _filter_courses_for_user,
    _filter_course_linked_obj_for_user,
    _filter_participation_linked_obj_for_user)

# }}}


from image_upload.models import FlowPageImage

from image_upload.utils import AdminMarkdownWidget

from markdownx.widgets import AdminMarkdownxWidget

class FPIWidget(AdminMarkdownxWidget):
    class Media:
        js = ("/static/marked/marked.min.js",)

class FPIAdminForm(forms.ModelForm):
    image_text = forms.CharField(
        widget=AdminMarkdownWidget, required=False, label=_("Related Html"))

    class Meta:
        model = FlowPageImage
        fields = ['image_text', 'is_image_textify', 'image_data', 'use_image_data'
                  ]

class HasImageTextFilter(admin.SimpleListFilter):
    title = _("Has image text?")
    parameter_name = 'hastext'
    def lookups(self, request, model_admin):
        return(
            ('y', _('Yes')),
            ('n', _('No')))
    def queryset(self, request, queryset):
        if self.value() == 'has_text':
            return queryset.filter(image_text__len__gt=0)
        else:
            return queryset.filter(image_text__len=0)

class ParticipationTagFilter(admin.SimpleListFilter):
    title = _("participation tags")
    parameter_name = 'ptags'

    def lookups(self, request, model_admin):
        from course.models import ParticipationTag
        ptag_qs = ParticipationTag.objects.all()
        ptag_list = [ptag.name for ptag in ptag_qs]

        tag_tuple = ()

        for tag in ptag_list:
            if tag.strip() <> "" and tag <> '<<<NONE>>>':
                tag_tuple += (((tag, tag),))

        self.tag_tuple = tag_tuple

        return (('no_tag', _('no tag')),) + tag_tuple

    def queryset(self, request, queryset):
        has_tag_list = [tag for (tag, _) in self.tag_tuple]
        if self.value() in has_tag_list:
            return queryset.filter(flow_session__participation__tags__name__exact=self.value())
        else:
            # result for no_tag
            return queryset.exclude(flow_session__participation__tags__name__in=has_tag_list)


class AccessRuleTagFilter(admin.SimpleListFilter):
    title = _("Access Rule Tag")
    parameter_name = 'accessruletag'
    def lookups(self, request, model_admin):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("select distinct access_rules_tag from course_flowsession "
                "order by access_rules_tag")
        from course.grades import mangle_session_access_rule_tag, RULE_TAG_NONE_STRING
        session_rule_tags = [
                mangle_session_access_rule_tag(row[0]) for row in cursor.fetchall()]

        tag_tuple = ()

        for tag in session_rule_tags:
            if tag.strip() <> "" and tag <> RULE_TAG_NONE_STRING:
                tag_tuple += (((tag, tag),))

        self.tag_tuple = tag_tuple

        return (('no_tag', _('no tag')),) + tag_tuple

    def queryset(self, request, queryset):
        has_tag_list = [tag for (tag, _) in self.tag_tuple]

        if self.value() in has_tag_list:
            return queryset.filter(flow_session__access_rules_tag__exact=self.value())
        else:
            # result for no_tag
            return queryset.exclude(flow_session__access_rules_tag__in=has_tag_list)

class FlowPageImageAdmin(admin.ModelAdmin):
    change_form_template = 'image_upload/flowpageimage_change_form.html'
    form = FPIAdminForm

    def get_flow_id(self, obj):
        return obj.flow_session.flow_id
    get_flow_id.short_description = _("Flow ID")
    get_flow_id.admin_order_field = "flow_session__flow_id"

    def has_image_text(self, obj):
        return True if obj.image_text else False
    has_image_text.short_description = _("Has image text?")
    has_image_text.boolean = True

    def get_full_name(self, obj):
        return obj.flow_session.participation.user.get_full_name()
    get_full_name.short_description = pgettext("real name of a user", "Name")
    get_full_name.admin_order_field = "flow_session__participation__user__last_name"

    list_filter = (
        "course",
        "image_page_id",
        'is_image_textify',
        'use_image_data',
        'order',
        HasImageTextFilter,
        AccessRuleTagFilter,
        ParticipationTagFilter,
    )

    list_display = (
        'id',
        'course',
        'is_image_textify',
        'has_image_text',
        'use_image_data',
        'order',
        'creator',
        'get_full_name',
        'creation_time',
        "image_page_id",
        "get_flow_id",
    )
    list_display_links = ('id',)

    # default_filters = ('order__eq=0',
    #                    'flow_session__access_rules_tag__neq="NO-refer"',
    #                    )

    fields = (('admin_image','image_text', 'is_image_textify'), ('image_data', 'use_image_data'))
    readonly_fields = ('admin_image',)

    date_hierarchy = "creation_time"

    save_on_top = True

    search_fields = (
        "=id",
        "=flow_session__id",
        "flow_session__flow_id",
        "flow_session__participation__user__username",
        "flow_session__participation__user__first_name",
        "flow_session__participation__user__last_name",
    )

    def get_queryset(self, request):
        qs = super(FlowPageImageAdmin, self).get_queryset(request)
        qs = qs.filter(flow_session__in_progress=False)

        return qs

    def get_view_on_site_url(self, obj=None):
        if obj is None or not self.view_on_site:
            return None

        if callable(self.view_on_site):
            return self.view_on_site(obj)
        elif self.view_on_site and hasattr(obj, 'get_absolute_url'):
            from django.core.urlresolvers import reverse
            from course.models import FlowPageData

            try:
                ordinal = obj.get_page_ordinal()
                if ordinal is None:
                    return None
            except:
                return None

            return reverse('relate-view_flow_page', kwargs={
                'course_identifier': obj.course.identifier,
                'flow_session_id': obj.flow_session.id,
                'ordinal': ordinal
            })

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        preserved_filters = self.get_preserved_filters(request)
        filtered_query_set = self.get_filtered_queryset(request)
        previous_fpi_id = None
        next_fpi_id = None
        for index, item in enumerate(filtered_query_set):
            if item.id == int(obj.id):
                if index > 0:
                    previous_fpi_id = filtered_query_set[index - 1].id
                if index + 1 < len(filtered_query_set):
                    next_fpi_id = filtered_query_set[index + 1].id

        if next_fpi_id is not None:
            context.update({"next_fpi_id": next_fpi_id})
        if previous_fpi_id is not None:
            context.update({"previous_fpi_id": previous_fpi_id})

        if obj:
            context.update({'course_identifier': obj.course.identifier,
                           'flow_session_id': obj.flow_session_id,
                           'ordinal': obj.get_page_ordinal()
                           })

        context.update({"preserved_filters": preserved_filters})
        return super(FlowPageImageAdmin,self)\
            .render_change_form(request, context, add, change, form_url, obj)

    def get_filtered_queryset(self, request):
        from django.contrib.admin.views.main import ERROR_FLAG
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)
        list_select_related = self.get_list_select_related(request)
        query_dict = self.get_query_dict(request)

        cl = None
        filtered_query_set = None
        try:
            cl = ChangeQuery(query_dict, request, self.model, list_display,
                            list_display_links, list_filter, self.date_hierarchy,
                            search_fields, list_select_related, self.list_per_page,
                            self.list_max_show_all, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.

            if ERROR_FLAG in request.GET.keys():
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })

        if cl:
            filtered_query_set = cl.get_queryset(request)

        return filtered_query_set

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = self.model._meta
        filtered_query_set = self.get_filtered_queryset(request)
        preserved_filters = self.get_preserved_filters(request)
        previous_fpi_id = None
        next_fpi_id = None
        for index, item in enumerate(filtered_query_set):
            if item.id == obj.id:
                if index > 0:
                    previous_fpi_id = filtered_query_set[index - 1].id
                if index + 1 < len(filtered_query_set):
                    next_fpi_id = filtered_query_set[index + 1].id

        if request.POST.has_key("_saveviewnext"):
            from django.utils.encoding import force_unicode
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            if next_fpi_id:
                self.message_user(request, msg)
                return HttpResponseRedirect("../../%s/change/?%s" % (next_fpi_id, preserved_filters))

        if request.GET.has_key("_viewnext"):
            from django.utils.encoding import force_unicode
            if next_fpi_id:
                return HttpResponseRedirect("../../%s/change/?%s" % (next_fpi_id, preserved_filters))

        if request.POST.has_key("_saveviewprevious"):
            from django.utils.encoding import force_unicode
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_unicode(obj._meta.verbose_name),
                    'obj': force_unicode(obj)})
            if previous_fpi_id:
                self.message_user(request, msg)
                return HttpResponseRedirect("../../%s/change/?%s" % (previous_fpi_id, preserved_filters))

        if request.GET.has_key("_viewprevious"):
            if previous_fpi_id:
                self.message_user(request, msg)
                return HttpResponseRedirect("../../%s/change/?%s" % (previous_fpi_id, preserved_filters))
        return super(FlowPageImageAdmin, self).response_change(request, obj)

    def get_query_dict(self, query_dict):
        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(query_dict)
        match = query_dict.resolver_match

        # get post url borrowed from modelAdmin.response_post_save_change()
        if self.has_change_permission(query_dict, None):
            url = reverse('admin:%s_%s_changelist' %
                               (opts.app_label, opts.model_name),
                               current_app=self.admin_site.name)
            preserved_filters = self.get_preserved_filters(query_dict)
            url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, url)
        else:
            url = reverse('admin:index',
                               current_app=self.admin_site.name)

        parsed_url = list(urlparse(url))
        parsed_qs = dict(parse_qsl(parsed_url[4]))
        merged_qs = dict()

        if opts and preserved_filters:
            preserved_filters = dict(parse_qsl(preserved_filters))

            match_url = '/%s' % url.partition(get_script_prefix())[2]
            try:
                match = resolve(match_url)
            except Resolver404:
                pass
        merged_qs.update(parsed_qs)
        return merged_qs

admin.site.register(FlowPageImage, FlowPageImageAdmin)


# This class is used to get querset in change_form
class ChangeQuery(ChangeList):
    def __init__(self, query_dict, *args, **kargs):
        self.query_dict = query_dict
        try:
            super(ChangeQuery,self).__init__(*args, **kargs)
        except IncorrectLookupParameters:
            self.params = self.query_dict