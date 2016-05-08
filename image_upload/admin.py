from django.contrib import admin

# Register your models here.
from image_upload.models import FlowPageImage


class FlowPageImageAdmin(admin.ModelAdmin):
    list_filter = ("course", "image_page_id", 'is_image_textify', 'use_image_data')
    list_display = ('course', 'is_image_textify', 'use_image_data', 'creator', 'creation_time', "image_page_id", "flow_session")

    fields = ('admin_image','image_text', 'is_image_textify', 'image_data', 'use_image_data'
              )
    readonly_fields = ('admin_image',)

    # {{{ permissions

    def get_queryset(self, request):
        from django.db.models import Max
        qs = super(FlowPageImageAdmin, self).get_queryset(request)
        qs = qs.filter(order=0).filter(flow_session__in_progress=False)\
            .exclude(flow_session__access_rules_tag__exact="NO-refer")\
            .exclude(flow_session__participation__tags__name__exact="Foreign")
            #.order_by('creator__id', 'creation_time').distinct('creator__id')


        #x = qs.values("course", 'creator__id', "image_page_id").annotate(latest_date=Max('creation_time'))

        return qs

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "course":
    #         kwargs["queryset"] = _filter_courses_for_user(
    #                 Course.objects, request.user)
    #     return super(FlowPageImageAdmin, self).formfield_for_foreignkey(
    #             db_field, request, **kwargs)

    # }}}

admin.site.register(FlowPageImage, FlowPageImageAdmin)
