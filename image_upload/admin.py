from django.contrib import admin

# Register your models here.
from image_upload.models import FlowPageImage


class FlowPageImageAdmin(admin.ModelAdmin):
    list_filter = ("course","flow_session")
    list_display = ('course', 'creator', 'admin_image')

    # {{{ permissions

    # def get_queryset(self, request):
    #     qs = super(FlowPageImageAdmin, self).get_queryset(request)
    #     return _filter_course_linked_obj_for_user(qs, request.user)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "course":
    #         kwargs["queryset"] = _filter_courses_for_user(
    #                 Course.objects, request.user)
    #     return super(FlowPageImageAdmin, self).formfield_for_foreignkey(
    #             db_field, request, **kwargs)

    # }}}

admin.site.register(FlowPageImage, FlowPageImageAdmin)
