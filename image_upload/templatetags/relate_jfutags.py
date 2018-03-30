from django.template.context_processors import csrf
from django.urls import reverse
from django.template import Library, loader

register = Library()


@register.simple_tag(takes_context=True)
def jfu(
        context,
        template_name='image_upload/upload-form-wrapper.html',
        upload_handler_name='jfu_upload',
        uploaded_view_name='jfu_view',
        *args, **kwargs
        ):
    """
    Displays a form for uploading files using jQuery File Upload.

    A user may use both a custom template or a custom upload-handling URL
    name by supplying values for template_name and upload_handler_name
    respectively.

    Any additionally supplied positional and keyword arguments are directly
    forwarded to the named custom upload-handling URL.
    """
    context.update({
        'JQ_OPEN': '{%',
        'JQ_CLOSE': '%}',
        'upload_handler_url': reverse(
            upload_handler_name, args=args, kwargs=kwargs
        ),
    })

    # The uploaded results are not displayed by default. To display the
    # uploaded results, pass the name of the view url to context.
    uploaded_view_url = reverse(uploaded_view_name, args=args, kwargs=kwargs)
    if context.get('prev_visit_id', None):
        uploaded_view_url += "?visit_id=%s" % context['prev_visit_id']

    # Use the request context variable, injected
    # by django.core.context_processors.request,
    # to generate the CSRF token.
    context['uploaded_view_url'] = uploaded_view_url
    context.update(csrf(context.get('request')))
    t = loader.get_template(template_name)
    return t.render(context.flatten())
