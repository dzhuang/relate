$(document).ready(function () {
    'use strict';
    $(".relate-save-button").each(function () {
        $(this).attr("formaction", window.location.pathname).detach().appendTo('#real-submit-div');
    }).on("click", function () {
        var all_pks = [];
        $("#img-presentation-table").find('tr').each(function () {
            all_pks.push($(this).attr("data-file-pk"));
            $("#div_id_hidden_answer").html(
                '<div class="controls">' +
                '<input type="hidden"' +
                ' id="id_hidden_answer" name="hidden_answer" type="text" value="'
                + all_pks +
                '"></div>');
        });
        $("#id_hidden_answer").prop("value", all_pks);
    });

    new Clipboard('.btn-data-copy');
    var input_changed = false;
    $('#img-presentation-table')
        .find("tbody").sortable(
        {
            delay: 500,
            handle: ".imageSortableHandle",
            scrollSpeed: 40,
            scrollSensitivity: 10,
            helper: "clone",
            axis: "y",
            opacity: 0.9,
            cursor: "move",
            // cursorAt: { bottom: 0},
            activate: function () {
                // $(controlElement).addClass("hidden");
                // $('.imageSortableHandle').removeClass("hidden");
            },
            deactivate: function () {
                // $(controlElement).removeClass("hidden");
                // $('.imageSortableHandle').addClass("hidden");
            }
        });
});


function disable_submit_button(bool) {
    var submit_button = document.getElementById("submit-id-submit");
    if (submit_button) {
        submit_button.disabled = bool;
    }
}

function disable_fileupload_control_button(bool) {
    var buttonbar = $('.fileupload-buttonbar');
    var start_button = $(buttonbar).find('.start')[0];
    var cancel_button =  $(buttonbar).find('.cancel')[0];
    if (start_button) {
        start_button.disabled = bool;
    }
    if (cancel_button) {
        cancel_button.disabled = bool;
    }
}

function toggle_fileupload_control_delete() {
    if(!getWidthQueryMatch_sm_xs()){
        var bulkdeletebutton = $('.fileupload-buttonbar').find('.delete')[0];
        if (bulkdeletebutton){
            bulkdeletebutton.disabled = $("#fileupload").find("[type='checkbox']:checked").length === 0;}
    }
}

function disable_fileupload_control_delete_checkbox(bool) {
    if(!getWidthQueryMatch_sm_xs()){
        var $checkbox = $(".fileupload-buttonbar").find("input[type='checkbox']")[0];
        if(bool){$checkbox.checked = false;}
        $checkbox.disabled = bool;
    }
}

function getWidthQueryMatch_md_sm_xs() {
    return window.matchMedia("(max-width: 1023px)").matches;
}

function getWidthQueryMatch_sm_xs() {
    return window.matchMedia("(max-width: 767px)").matches;
}

function formatFileSize(bytes) {
    if (typeof bytes !== 'number') {
        return '';
    }
    if (bytes >= 1000000000) {
        return (bytes / 1000000000).toFixed(2) + ' GB';
    }
    if (bytes >= 1000000) {
        return (bytes / 1000000).toFixed(2) + ' MB';
    }
    return (bytes / 1000).toFixed(2) + ' KB';
}

function generateImageMobileDescription(row_element) {
    var shortInfo = row_element.find(".name").text();
    var file_pk = row_element.data("file-pk");
    var file_size = row_element.find(".size").text();
    var file_time = row_element.find(".timestr").text();
    // var detailedInfo = file_time + "(" + file_size +")";
    row_element.children(".fileUploadCompactInfo").html(
        '<p style="width: 30vw;">'
        + shortInfo
        + '<span '
        + 'onclick=\"$(\'#moreinfo' + file_pk  + '\').toggle(); return false;"'
        + '>...</span>'
        + '</p>'
        + '<div style="display: none;"'
        + ' id="moreinfo' + file_pk
        + '\">'
        + '<p style="width: 30vw;">'
        +  file_time
        + '</p>'
        + '<p style="width: 30vw;">'
        +  file_size
        + '</p>'
        + '</div>'
    );
}

// close gallery using back button
$('#blueimp-gallery')
    .on('open', function (e) {
        if (getWidthQueryMatch_md_sm_xs()) {
            window.history.pushState('forward', null, '#slides');
        }
    })
    .on('close', function (e) {
        if (location.hash == '#slides' && getWidthQueryMatch_md_sm_xs()) window.history.back();
    });


window.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var modal_html = $('#editPopup').html();
    console.log("modal loaded.");

    var $image, contData, result, ajax_url, target_image_pk, scrollPos;
    var $updatedTableRow, $updatedPreview, $updatedThumbnail, $updatedFilename,
        $updatedFileSize, $updatedFileTime, $updatedDeleteUrl, $editTarget;

    $('#editPopup').on('show.bs.modal', function (e) {

         $(this).find('.modal-body').css({
              width:'auto', //probably not needed
              height:'auto', //probably not needed
              'max-height':'100%'
       });

        $editTarget = $(e.relatedTarget);
        var target_image_pk = $editTarget.attr('data-pk');
        var image_src = $editTarget.attr('data-src');

        $image = $("#image");
        $image.attr("src", image_src);
        $updatedTableRow = $editTarget.parents("tr");
        $updatedPreview = $("#previewid" + target_image_pk);
        $updatedThumbnail = $("#thumbnail" + target_image_pk);
        $updatedFilename = $("#filename" + target_image_pk);
        $updatedFileSize = $("#filesize" + target_image_pk);
        $updatedFileTime = $("#filetime" + target_image_pk);
        $updatedDeleteUrl = $("#deleteurl" + target_image_pk);
        ajax_url = $editTarget.attr("data-action");

        // prevent background scrolling
        // http://stackoverflow.com/a/34754029/3437454
        scrollPos = $('body').scrollTop();
        $('body').css({
            overflow: 'hidden',
            position: 'fixed',
            top : -scrollPos
        });

    })
        .on('shown.bs.modal', function () {
            $(".relate-save-button").addClass('disabled');

            $image.cropper({
                checkOrientation: false,
                autoCrop: true,
                autoCropArea: 1,
                strict: true,
                movable: false,
                zoomable: false,
                minContainerheight: $(window).height() * 0.8,
                ready: function (data) {
                    $image.cropper('setContainerData', contData);
                    $(".btn-crp-rtt").removeClass("disabled");
                },
                cropstart: function (data) {
                    $('.btn-crp-submit').removeClass("disabled");
                    $('.btn-crp-reset').removeClass("disabled");
                },
                crop: function (data) {
                    result = data;
                },
                rotate: function (data) {

                }
            });

            function crpMsg(success, msg) {
                var e = $("#crp-result");
                if (success === true) {
                    e.addClass('alert alert-success').html(msg);
                } else {
                    e.addClass('alert alert-danger').html(msg);
                }
                window.setTimeout(function () {
                    e.removeClass().html("");
                }, 3000);
            }

            function rtt(angle) {
                var canvData, newWidth, newHeight, newCanvData;
                contData = $image.cropper('getContainerData');
                $image.cropper('setCropBoxData', {
                    width: 2,
                    height: 2,
                    top: (contData.height / 2) - 1,
                    left: (contData.width / 2) - 1
                });

                $image.cropper('rotate', angle);

                canvData = $image.cropper('getCanvasData');
                newWidth = canvData.width * (contData.height / canvData.height);

                if (newWidth >= contData.width) {
                    newHeight = canvData.height * (contData.width / canvData.width);
                    newCanvData = {
                        height: newHeight,
                        width: contData.width,
                        top: (contData.height - newHeight) / 2,
                        left: 0
                    };
                } else {
                    newCanvData = {
                        height: contData.height,
                        width: newWidth,
                        top: 0,
                        left: (contData.width - newWidth) / 2
                    };
                }

                $image.cropper('setCanvasData', newCanvData);
                $image.cropper('setCropBoxData', newCanvData);

                $('.btn-crp-submit').removeClass("disabled");
                $('.btn-crp-reset').removeClass("disabled");
            }

            $(".btn-crp-rtt").click(function () {
                rtt($(this).data("option"));
            });

            $('.btn-crp-preview').click(function () {
                var toggle = $('.cropper-container').hasClass("hidden"),
                    result = $image.cropper('getCroppedCanvas');
                if (!toggle) {
                    $('.cropper-container').addClass("hidden");
                    $('#preview').removeClass("hidden").html(result);
                    $(this).html("<i class='fa fa-pencil'></i> <span>" + gettext('Edit') + "</span>");
                    $(".btn-crp-rtt").addClass("hidden");
                    $(".btn-crp-reset").addClass("hidden");
                } else {
                    $('.cropper-container').removeClass("hidden");
                    $('#preview').addClass("hidden").html("");
                    $(this).html("<i class='fa fa-eye'></i> <span>" + gettext('Preview') + "</span>");
                    $(".btn-crp-rtt").removeClass("hidden");
                    $(".btn-crp-reset").removeClass("hidden");
                }
            });

            $('.btn-crp-submit').click(function () {
                $(this).addClass("disabled");
                $(".modal-footer > button").addClass("disabled");
                var jqxhr = $.ajax({
                    method: "POST",
                    url: ajax_url,
                    data: JSON.stringify($image.cropper("getData")),
                    beforeSend: function (xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", $editTarget.attr("data-data"));
                    }
                })
                    .done(function (response) {
                        var new_img = response.file;
                        $updatedThumbnail.prop("id", "thumbnail" + new_img.pk).parents("span").addClass("processing");
                        if (window.location.pathname.indexOf("/grading/") === -1) {
                            $updatedThumbnail.removeClass("hidden").prop('src', new_img.thumbnailUrl);
                        } else {
                            $updatedThumbnail.prop('src', new_img.url).prop('style', "width:40vw");
                        }
                        $updatedTableRow.attr("data-file-pk", new_img.pk);
                        $updatedPreview.prop("id", "previewid" + new_img.pk).prop('href', new_img.url);
                        $updatedFilename.prop("id", "filename" + new_img.pk).prop('href', new_img.url);
                        $updatedFileTime.prop("id", "filetime" + new_img.pk).prop('title', new_img.timestr_title).html(new_img.timestr_short);
                        $updatedFileSize.prop("id", "filesize" + new_img.pk).html(formatFileSize(new_img.size));
                        $updatedDeleteUrl.prop("id", "deleteurl" + new_img.pk).attr('data-url', new_img.deleteUrl);
                        $editTarget.attr("data-src", new_img.url).attr("data-action", new_img.crop_handler_url).attr("data-pk", new_img.pk);
                        generateImageMobileDescription($updatedTableRow);

                        $image.cropper('replace', new_img.url);
                        crpMsg(true, gettext('Done!'));
                        setTimeout(function () {
                            $('#editPopup').modal('hide');
                        }, 2000);
                        $('#fileupload').trigger("file_edited");
                    })
                    .fail(function (response) {
                        var msg = gettext('Failed!') + " " + response.responseJSON.message;
                        crpMsg(false, msg);
                        setTimeout(function () {
                            $('#editPopup').modal('hide');
                        }, 2000);
                    });
                return false;
            });

            $('.btn-crp-reset').click(function () {
                $image.cropper('reset');
                $('.btn-crp-submit').addClass("disabled");
                $('.btn-crp-reset').addClass("disabled");
            });

        })
        .on('hidden.bs.modal', function () {
            $(".relate-save-button").removeClass('disabled');
            $image.cropper('destroy');
            $(this).html(modal_html);
            $('#preview').addClass("hidden").html("");
        })
        .on('show.bs.modal', function (e) {
            // Enable back button to close modal and blueimp gallery
            // http://stackoverflow.com/a/40364619/3437454
            if (getWidthQueryMatch_md_sm_xs()) window.history.pushState('forward', null, '#edit');
            })
        .on('hide.bs.modal', function (e) {
            if (location.hash === '#edit' && getWidthQueryMatch_md_sm_xs()) window.history.back();

            $('body').css({
                overflow: '',
                position: '',
                top: ''
            }).scrollTop(scrollPos);
        });

    $(window).on('popstate', function (event) {  //pressed back button
        if (event.state && getWidthQueryMatch_md_sm_xs()) {
            var gallery = $('#blueimp-gallery').data('gallery');
            if (gallery) {
                gallery.close();
            }
            else {
                $('.modal').modal('hide');
            }
        }
    });
});


function activate_change_listening() {
    var input_changed = false;

    function on_input_change(evt) {
        input_changed = true;
    }

    $(":file").on("change", on_input_change);
    $(window).on('beforeunload',
        function () {
            if (input_changed)
                return "{% trans 'You have unsaved changes on this page.' %}";
        });

    $('#img-presentation-table').children("tbody").on("sortchange", on_input_change);

    $('#fileupload')
        .on("fileuploadloadingexistalways", function () {
            $(".fileupload-download-processing").remove();
        })
        .on("file_edited fileuploaddestroyed", on_input_change)
        .on("fileuploadcompleted fileuploaddestroyed", function () {
            var n_exist_file = $('.template-download').length;
            disable_fileupload_control_delete_checkbox(n_exist_file === 0);
            if (n_exist_file > 1) {
                $('.imageSortableHandle').removeClass("hidden");
            } else {
                $('.imageSortableHandle').addClass("hidden");
            }
        })
        .on("fileuploadadd", function (e, data) {
            disable_submit_button(true);
            disable_fileupload_control_button(false);
        })
        .on("fileuploadadded", function (e, data) {
            // disable_fileupload_control_button(false);
        })
        .on("fileuploadcompleted", function (e, data) {
            if(getWidthQueryMatch_sm_xs()){
                $(this).find("canvas").each(function(){
                    updateCanvasCss(this);
                });
            }
        })
        .on("fileuploaddestroyed", toggle_fileupload_control_delete)
        .on("fileuploadfailed fileuploadcompleted fileuploaddestroyed", function () {
            var queue_length = $('.template-upload').length;
            disable_submit_button(queue_length > 0);
            disable_fileupload_control_button(queue_length === 0);
        })
        .on('fileuploadprocessstart', function () {
            // console.log('processstart');
        })
        .on('fileuploadprocessalways', function (e, data) {
            var el = data.files[data.index].preview;
            if(getWidthQueryMatch_sm_xs()){updateCanvasCss(el);}
        });

        $('body').on('change','#fileupload input[type="checkbox"]',function(e){
            // e.preventDefault();
            // e.stopPropagation();
            toggle_fileupload_control_delete();
        });

        function updateCanvasCss(element) {
            var parent_width, new_height;
            parent_width = $(element).parents("td").width();
            if (!parent_width){
                setTimeout(function(){updateCanvasCss(element)}, 50);
            }
            else{
                new_height = parent_width * (element.height/element.width);
                $(element).css({"width": "100%", "height": new_height});
            }
        }

    function before_submit(evt) {
        input_changed = false;

        // We can't simply set "disabled" on the submitting button here.
        // Otherwise the browser will simply remove that button from the POST
        // data.

        $(".relate-save-button").each(
            function () {
                var clone = $(this).clone();
                $(clone).attr("disabled", "1");
                $(this).after(clone);
                $(this).hide();
            });
    }

    $(".relate-interaction-container form").on("submit", before_submit);
}

$(document).ready(activate_change_listening);