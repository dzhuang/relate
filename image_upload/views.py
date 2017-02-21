# -*- coding: utf-8 -*-

from __future__ import division

__copyright__ = "Copyright (C) 2016 Dong Zhuang"

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

import os

from django.shortcuts import get_object_or_404
from django.conf import settings
from django import forms, http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.views.generic import (
        CreateView, DeleteView, ListView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _, string_concat, ugettext
from django.db import transaction

from course.models import Course, FlowPageData, FlowSession
from course.utils import course_view

from image_upload.serialize import serialize
from image_upload.utils import get_page_image_behavior, ImageOperationMixin
from image_upload.models import FlowPageImage
from image_upload.storages import UserImageStorage

from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from braces.views import JSONResponseMixin
import json
from PIL import Image
from io import BytesIO
from sendfile import sendfile
from pymongo.errors import DuplicateKeyError

storage = UserImageStorage()
protected_root = getattr(settings, "SENDFILE_ROOT")


def is_course_staff(pctx):
    request = pctx.request
    course = pctx.course

    from course.enrollment import (
        get_participation_for_request,
        get_participation_permissions)

    participation = get_participation_for_request(request, course)

    perms = get_participation_permissions(course, participation)
    from course.constants import participation_permission as pperm
    if (pperm.assign_grade, None) in perms:
        return True

    return False


class ImageCreateView(LoginRequiredMixin, ImageOperationMixin,
                      JSONResponseMixin, CreateView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454
    content_type = 'text/plain'
    model = FlowPageImage
    fields = ("image", "slug")

    def form_valid(self, form):
        image = form.cleaned_data.get('image')
        from django.conf import settings

        max_allowed_jfu_size = getattr(
            settings, "RELATE_JFU_MAX_IMAGE_SIZE", 2) * 1024**2

        if image._size > max_allowed_jfu_size:
            file_data = {
                    "files": [{
                        "name": form.cleaned_data.get('slug'),
                        "size": image._size,
                        "error": ugettext(
                            "The image is too big. Please use "
                            "Chrome/Firefox or mobile browser by "
                            "which images will be cropped "
                            "automatically before upload.")
                        },
                    ]}

            return self.render_json_response(file_data)

        self.object = form.save(commit=False)
        self.object.creator = self.request.user

        course_identifier = self.kwargs["course_identifier"]
        course = get_object_or_404(Course, identifier=course_identifier)
        flow_session_id = self.kwargs["flow_session_id"]
        ordinal = self.kwargs["ordinal"]

        fpd = FlowPageData.objects.get(flow_session=flow_session_id, ordinal=ordinal)
        self.object.flow_session_id = flow_session_id
        self.object.image_page_id = fpd.page_id
        self.object.course = course
        self.object.save()

        files = [serialize(self.request, self.object, 'image')]
        data = {'files': files}
        return self.render_json_response(data)

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return self.render_json_response(data, status=400)


class ImageItemForm(forms.ModelForm):
    class Meta:
        model = FlowPageImage
        fields = ("image",)


class ImageDeleteView(LoginRequiredMixin, ImageOperationMixin, DeleteView):
    model = FlowPageImage

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.creator:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_("may not delete other people's image"))
        else:
            if storage.is_temp_image(self.object.image.file.name):
                self.object.delete()
                response = http.JsonResponse(True, safe=False)
            else:
                response = http.JsonResponse(False, safe=False)
            response['Content-Disposition'] = 'inline; filename=files.json'
            response['Content-Type'] = 'text/plain'
            return response


class ImageListView(LoginRequiredMixin, JSONResponseMixin, ListView):
    # Prevent download Json response in IE 7-10
    # http://stackoverflow.com/a/13944206/3437454):
    model = FlowPageImage

    def get_queryset(self):
        flow_session_id = self.kwargs["flow_session_id"]
        flow_session = get_object_or_404(FlowSession, id=int(flow_session_id))
        ordinal = self.kwargs["ordinal"]
        course_identifier = self.kwargs["course_identifier"]
        from course.utils import CoursePageContext
        pctx = CoursePageContext(self.request, course_identifier)
        prev_visit_id = self.request.GET.get("visit_id")

        if prev_visit_id is not None:
            try:
                prev_visit_id = int(prev_visit_id)
            except ValueError:
                from django.core.exceptions import SuspiciousOperation
                raise SuspiciousOperation("non-integer passed for 'visit_id'")
        from course.utils import FlowPageContext
        from course.flow import get_prev_answer_visits_qset
        fpctx = FlowPageContext(
            repo=pctx.repo,
            course=pctx.course,
            flow_id=flow_session.flow_id,
            ordinal=int(ordinal),
            flow_session=flow_session,
            participation=flow_session.participation,
            request=self.request
        )

        prev_answer_visits = list(
                get_prev_answer_visits_qset(fpctx.page_data))

        # {{{ fish out previous answer_visit

        if prev_answer_visits and prev_visit_id is not None:
            answer_visit = prev_answer_visits[0]

            for ivisit, pvisit in enumerate(prev_answer_visits):
                if pvisit.id == prev_visit_id:
                    answer_visit = pvisit
                    break

        elif prev_answer_visits:
            answer_visit = prev_answer_visits[0]

        else:
            answer_visit = None

        # }}}

        if not answer_visit:
            return None

        answer_data = answer_visit.answer

        if not answer_data:
            return None

        pk_list = []

        # {{{ to be removed

        if not isinstance(answer_data, dict):
            fpd = None
            try:
                fpd = FlowPageData.objects.get(
                    flow_session=flow_session_id, ordinal=ordinal)
            except ValueError:
                # in sandbox
                if flow_session_id == "None" or ordinal == "None":
                    return None

            if not fpd:
                return None

            qs = (FlowPageImage.objects.filter(
                flow_session=flow_session_id,
                image_page_id=fpd.page_id)
                  .order_by("order", "pk"))

            if not qs:
                return None

            will_save_new_data = True
            for q in qs:
                a = json.loads(answer_data)
                if repr(q) in a:
                    pk_list.append(q.pk)
                else:
                    will_save_new_data = False
                    pk_list = []
                    break

            if not pk_list:
                return None

            if not will_save_new_data:
                return None
            else:
                new_answer_data = {"answer": pk_list}

                for img_pk in pk_list:
                    img = FlowPageImage.objects.get(pk=img_pk)
                    full_path = img.image.file.name
                    if not os.path.isfile(full_path):
                        raise ValueError(
                            "FlowPageImage %s (%s) does't have a"
                            " valid path %s " % img, img.pk, full_path)

                    original_storage_path = img.image.name
                    exist = storage.meta_backend.exists(path=full_path)
                    if exist:
                        obj = storage.meta_backend.get(path=full_path)
                        obj.update(
                            {
                                "original_name": full_path,
                                "path": full_path,
                                "original_storage_path": original_storage_path,
                                'original_storage_name': "sendfile"
                            }
                        )
                    else:
                        data = storage.get_data_for_meta_backend_save(
                            original_name=full_path,
                            path=full_path,
                            content=img.image,
                            original_storage_path=original_storage_path,
                        )
                        data.update({
                            'original_storage_name': "sendfile"
                        })

                        storage.meta_backend.create(data=data)

                    answer_visit.answer = new_answer_data
                    answer_visit.save()

            #  to be removed }}}

        if not pk_list:
            pk_list = answer_data.get("answer", None)
        if not pk_list:
            return None

        # Creating a QuerySet from a list while preserving order using Django
        # https://codybonney.com/creating-a-queryset-from-a-list-while-preserving-order-using-django/
        clauses = (
            ' '.join(['WHEN id=%s THEN %s' % (pk, i)
                      for i, pk in enumerate(pk_list)]))
        ordering = 'CASE %s END' % clauses
        queryset = FlowPageImage.objects.filter(pk__in=pk_list).extra(
            select={'ordering': ordering}, order_by=('ordering',))

        return queryset

    def render_to_response(self, context, **response_kwargs):
        queryset = self.get_queryset()
        if queryset:
            files = [serialize(self.request, p, 'image')
                    for p in self.get_queryset()]
            data = {'files': files}
        else:
            data = {}
        return self.render_json_response(data)

# }}}


# {{{ sendfile

@login_required
def user_image_download(request, creator_id, download_id):
    # refer to the following method to allow staff download
    download_object = get_object_or_404(Image, pk=download_id)
    return _auth_download(request, download_object)


@login_required
@course_view
def flow_page_image_download(pctx, flow_session_id, creator_id,
                             download_id, file_name):
    request = pctx.request
    download_object = get_object_or_404(FlowPageImage, pk=download_id)

    if storage.is_temp_image(download_object.image.file.name):
        return _non_auth_download(request, download_object)

    privilege = False
    # whether the user is allowed to view the private image
    from course.constants import participation_permission as pperm
    if pctx.has_permission(pperm.assign_grade):
        privilege = True

    return _auth_download(request, download_object, privilege)


@login_required
def flow_page_image_problem(request, download_id, file_name):
    # show the problem image
    download_object = get_object_or_404(FlowPageImage, pk=download_id)
    if download_object.order == 0:
        privilege = True
    else:
        privilege = False
    return _auth_download(request, download_object, privilege)


@login_required
def flow_page_image_key(request, download_id, creator_id, file_name):
    download_object = get_object_or_404(FlowPageImage, pk=download_id)
    privilege = True
    return _auth_download(request, download_object, privilege)


@login_required
def _auth_download(request, download_object, privilege=False):
    if (not request.user == download_object.creator
        and
            not request.user.is_staff
        or
            not privilege):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))

    return sendfile(request, download_object.image.path)


@login_required
def _non_auth_download(request, download_object):
    if (not request.user == download_object.creator
        and
            not request.user.is_staff):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(_("may not view other people's resource"))

    from sendfile.backends.development import sendfile
    return sendfile(request, download_object.image.path)

# }}}


# {{{ crop image

class CropImageError(BadRequest):
    pass


@login_required
@course_view
def image_crop_modal(pctx, flow_session_id, ordinal, pk):
    request = pctx.request
    error_message = None
    try:
        image = FlowPageImage.objects.get(id=pk)
    except FlowPageImage.DoesNotExist:
        error_message = (
            string_concat(_('File not found.'),
                          _('Please upload the image first.')))
        return render(
            request,
            'image_upload/cropper-modal.html',
            {'image': None,
             'error_message': error_message,
             'STAFF_EDIT_WARNNING': False,
             'owner': None
             })
    course_staff_status = is_course_staff(pctx)
    staff_edit_warnning = False
    if (course_staff_status
        and
                request.user != image.creator):
        staff_edit_warnning = True
    return render(
        request,
        'image_upload/cropper-modal.html',
        {'image': image,
         'error_message': error_message,
         'STAFF_EDIT_WARNNING': staff_edit_warnning,
         'owner': image.creator
         })


@json_view
@login_required
@transaction.atomic
@course_view
def image_crop(pctx, flow_session_id, ordinal, pk):
    try:
        page_image_behavior = get_page_image_behavior(
            pctx, flow_session_id, ordinal)
        may_change_answer = page_image_behavior.may_change_answer
    except ValueError:
        may_change_answer = True

    course_staff_status = is_course_staff(pctx)
    request = pctx.request

    if not (may_change_answer or course_staff_status):
        raise CropImageError(_('Not allowd to modify answer.'))
    try:
        crop_instance = FlowPageImage.objects.get(pk=pk)
    except FlowPageImage.DoesNotExist:
        raise CropImageError(_('Please upload the image first.'))

    image_orig_path = crop_instance.image.path
    if not image_orig_path:
        raise CropImageError(
            string_concat(_('File not found.'),
                          _('Please upload the image first.')))

    if not request.POST:
        return {}

    if not request.is_ajax():
        raise CropImageError(_('Only Ajax Post is allowed.'))

    try:
        x = int(float(request.POST['x']))
        y = int(float(request.POST['y']))
        width = int(float(request.POST['width']))
        height = int(float(request.POST['height']))
        rotate = int(float(request.POST['rotate']))
    except:
        raise CropImageError(
            _('There are errors, please refresh the page '
              'or try again later'))

    try:
        new_image = Image.open(image_orig_path)
    except IOError:
        raise CropImageError(
            _('There are errors，please re-upload the image'))
    image_format = new_image.format

    if rotate != 0:
        # or it will raise "AttributeError: 'NoneType' object has no attribute
        # 'mode' error in pillow 3.3.0
        new_image = new_image.rotate(-rotate, expand=True)

    box = (x, y, x+width, y+height)
    new_image = new_image.crop(box)

    if new_image.mode != "RGB":
        new_image = new_image.convert("RGB")

    from relate.utils import as_local_time, local_now
    import datetime

    new_image_file_last_modified = crop_instance.creation_time
    if not course_staff_status:
        if local_now() > as_local_time(
                        crop_instance.creation_time + datetime.timedelta(minutes=5)):
            new_image_file_last_modified = local_now()

    new_image_io = BytesIO()
    new_image.save(new_image_io, format=image_format)

    new_instance = FlowPageImage()
    new_instance.creator = crop_instance.creator
    new_instance.image.save(
        name=crop_instance.slug,
        content=ContentFile(new_image_io.getvalue()),
        save=False
    )

    new_instance.slug = crop_instance.slug
    new_instance.creation_time = crop_instance.creation_time
    new_instance.file_last_modified = new_image_file_last_modified
    new_instance.course = crop_instance.course
    new_instance.flow_session = crop_instance.flow_session
    new_instance.image_page_id = crop_instance.image_page_id
    new_instance.is_image_textify = crop_instance.is_image_textify
    new_instance.image_text = crop_instance.image_text
    new_instance.image_data = crop_instance.image_data
    new_instance.use_image_data = crop_instance.use_image_data

    try:
        new_instance.save()
    except (OSError, IOError) as e:
        raise CropImageError(string_concat(
            _('There are errors, please refresh the page or try again later'),
            "--%s:%s." % (type(e).__name__, str(e))
        ))
    finally:
        new_image.close()

    response_file = serialize(request, new_instance, 'image')
    data = {'file': response_file}
    return data

# }}}


class ImgTableOrderError(BadRequest):
    pass


@json_view
@login_required
@transaction.atomic
@course_view
def image_order(pctx, flow_session_id, ordinal):
    try:
        page_image_behavior = get_page_image_behavior(
            pctx, flow_session_id, ordinal)
        may_change_answer = page_image_behavior.may_change_answer
    except ValueError:
        may_change_answer = True

    course_staff_status = is_course_staff(pctx)
    if not (may_change_answer or course_staff_status):
        raise ImgTableOrderError(_('Not allowd to modify answer.'))
    request = pctx.request

    if not request.POST:
        return {}

    if not request.is_ajax():
        raise ImgTableOrderError(_('Only Ajax Post is allowed.'))

    response = {'message': ugettext('Done')}

    return response


def get_rel_and_full_path(path, root=None):
    rel_path = None
    full_path = None
    if not root:
        root = protected_root

    if not os.path.isfile(path):
        rel_path = path
        full_path = os.path.join(root, path)
    else:
        full_path = path
        rel_path = os.path.relpath(full_path, root)
    return (rel_path.lstrip("/"), full_path)

# {{{ This should be removed as soon as all computer are migrated!

def migrate_to_meta_backend():
    """
    This is used to migrate FlowPageImage to ProxyStorage
    """
    all_images_qs = FlowPageImage.objects.all()
    i = 0
    for img in all_images_qs:
        i += 1
        print("%s/%s" % (i, len(all_images_qs)))
        try:
            full_path = img.image.file.name
        except FileNotFoundError:
            continue
        except:
            if img.pk in [1965, 1966, 1967]:
                continue
            print(img.pk)
            raise

        try:
            if storage.is_temp_image(img.image.file.name):
                continue
        except:
            pass

        if not os.path.isfile(full_path):
            raise ValueError(
                "FlowPageImage %s (%s) does't have a"
                " valid path %s " % (img, img.pk, full_path))

        original_storage_path = str(img.image)
        try:
            assert original_storage_path != full_path
        except:
            if "course_imgs/" in full_path:
                continue
            if original_storage_path.startswith("/srv/www/relate/protected/"):
                original_storage_path = original_storage_path.replace(
                    "/srv/www/relate/protected/", "")
            else:
                print("Full_path:", full_path)
                print("Relative_path:", original_storage_path)
                raise ValueError(
                    "FlowPageImage %s (%s) does't have a"
                    " valid path %s" % (img, img.pk, full_path))

        try:
            assert original_storage_path in full_path
        except:
            print("Full_path:", full_path)
            print("Relative_path:", original_storage_path)

            raise ValueError(
                "FlowPageImage %s (%s) does't have a"
                " valid path %s" % (img, img.pk, full_path))

        exist = storage.meta_backend.exists(path=full_path)
        if exist:
            obj = storage.meta_backend.get(path=full_path)
            obj.update(
                {
                    "original_name": full_path,
                    "path": full_path,
                    "original_storage_path": original_storage_path,
                    'original_storage_name': "sendfile"
                }
            )
        else:
            data = storage.get_data_for_meta_backend_save(
                original_name=full_path,
                path=full_path,
                content=img.image,
                original_storage_path=original_storage_path,
            )
            data.update({
                'original_storage_name': "sendfile"
            })

            storage.meta_backend.create(data=data)


def migrate_answer_data():
    """
    This is used to migrate answer_data to meet ProxyStorage
    """
    from course.models import FlowPageData
    from course.flow import get_prev_answer_visits_qset
    data = FlowPageData.objects.filter(
        flow_session__course__identifier__in=["OR2016BA", "OR2016IE"]
    ).order_by("pk")
    i = 0
    for d in data:
        i += 1
        print("%s/%s" % (i, len(data)))
        all = list(get_prev_answer_visits_qset(d))
        if not len(all):
            continue
        for answer_visit in all:
            answer_data = answer_visit.answer
            if not answer_data:
                continue

            if isinstance(answer_data, dict):
                continue

            print(answer_data)
            print(answer_visit.id)

            if "<QuerySet" not in answer_data:
                print("passed------------------------")
                continue

            pk_list = []
            fpd = FlowPageData.objects.get(
                flow_session=d.flow_session_id, ordinal=d.ordinal)

            if not fpd:
                continue

            qs = (FlowPageImage.objects.filter(
                flow_session=fpd.flow_session_id,
                image_page_id=fpd.page_id)
                  .order_by("order", "pk"))

            if not qs:
                continue

            will_save_new_data = True
            for q in qs:
                x = json.loads(answer_data)
                p = str(repr(q)).split(" ")[1]
                if p in x:
                    pk_list.append(q.pk)
                    print("--added--")
                else:
                    print("------alert-------")
                    print("%s not in %s" % (p, x))
                    will_save_new_data = False
                    pk_list = []
                    break

            if not pk_list:
                continue

            if not will_save_new_data:
                continue
            else:
                new_answer_data = {"answer": pk_list}
                answer_visit.answer = new_answer_data
                answer_visit.save()
# }}}
