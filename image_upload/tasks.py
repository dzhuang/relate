# -*- coding: utf-8 -*-

from __future__ import division, absolute_import

__copyright__ = "Copyright (C) 2017 Dong Zhuang"

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

from celery import shared_task
from image_upload.models import FlowPageImage


@shared_task(bind=True)
def delete_temp_images_from_submitted_page(self, flow_session_id, page_id):
    # delete temp images upon page submission
    fpi_qs = FlowPageImage.objects.filter(
        flow_session_id=flow_session_id,
        image_page_id=page_id,
        is_temp_image=True
    )
    for FPI in fpi_qs:
        FPI.refresh_from_db()
        if FPI.is_temp_image:
            FPI.delete()
