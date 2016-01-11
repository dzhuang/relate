# encoding: utf-8
import mimetypes
import re
from django.core.urlresolvers import reverse


def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 20:
        return name
    return name[:10] + "..." + name[-7:]


def serialize(instance, file_attr='file', flow_session_id=None, ordinal=None):
    """serialize -- Serialize a Picture instance into a dict.

    instance -- Picture instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    from django.conf import settings
    
    from django.conf.urls.static import static

    obj = getattr(instance, file_attr)
    
    #print type(instance)
    #print instance.get_absolute_url()

    return {
        #'url': obj.url,
        'url': instance.get_absolute_url(),
        'name': order_name(obj.name),
        'type': mimetypes.guess_type(obj.path)[0] or 'image/png',
        #'thumbnailUrl': obj.url,
        'thumbnailUrl': instance.get_absolute_url(),
        'size': obj.size,
        'deleteUrl':
        reverse('jfu_delete', kwargs={
                'pk':instance.pk, 
                'flow_session_id':flow_session_id, 
                'ordinal':ordinal}),
        'deleteType': 'POST',
    }


