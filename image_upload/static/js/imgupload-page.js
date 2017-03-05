$(document).ready(function () {
    'use strict';
    $(".relate-save-button").each(function () {
        $(this).attr("formaction", window.location.pathname).detach().appendTo('#real-submit-div');
    });
    // $('#past-submission_dropdown').addClass('hidden');
    new Clipboard('.btn-data-copy');
    var input_changed = false;

    // {{{ detect forward and backward
    // https://gist.github.com/sstephenson/739659
    // Failed for modal
    // var detectBackOrForward = function(onBack, onForward) {
    //   var hashHistory = [window.location.hash];
    //   var historyLength = window.history.length;
    //
    //   return function() {
    //     var hash = window.location.hash, length = window.history.length;
    //     if (hashHistory.length && historyLength == length) {
    //       if (hashHistory[hashHistory.length - 2] == hash) {
    //         hashHistory = hashHistory.slice(0, -1);
    //         onBack();
    //       } else {
    //         hashHistory.push(hash);
    //         onForward();
    //       }
    //     } else {
    //       hashHistory.push(hash);
    //       historyLength = length;
    //     }
    //   }
    // };

    // window.addEventListener("hashchange", detectBackOrForward(
    //   function() { console.log("back"); $(this).trigger("navigateBack"); },
    //   function() { console.log("forward"); $(this).trigger("navigateForward");  }
    // ));
    // }}}
});

var console_debug;

function disable_submit_button(bool) {
    var submit_button = document.getElementById("submit-id-submit");
    if(submit_button !== null){
        submit_button.disabled = bool;
    }
}

function getWidthQueryMatch() {
    return window.matchMedia("(max-width: 1023px)").matches;
}

function assignOrder() {
    'use strict';
    var idx = 0;
    $('#fileupload').children("table tbody tr").each(function () {
        $(this).data("order").new_ord = idx;
        idx = idx + 1;
    });
    $('.btn-srt').each(function () {
        $(this).removeClass("hidden");
    });
    $('tr:nth-child(1) > td.td-srt > .up').addClass("hidden");
    $('tr:nth-child(1) > td.td-srt > .top').addClass("hidden");
    $('tr:nth-child(2) > td.td-srt > .top').addClass("hidden");
    $('tr:nth-last-child(1) > td.td-srt > .down').addClass("hidden");
}

$('.btn-srt-tbl').on('click', function () {
    'use strict';
    var $up, $down, len, row1, row2, $top, chg_data, jqxhr;
    $(this).addClass('hidden');
    $('#fileupload > .fileupload-buttonbar > div > *').not('.btn-srt-tbl-cfm').not('.btn-srt-tbl').addClass('disabled');
    $('.btn-srt-tbl-cfm').removeClass('hidden');
    $('.td-dl').each(function () {
        $(this).addClass('hidden');
    });
    $('.td-srt').each(function () {
        $(this).removeClass('hidden');
    });

    assignOrder();

    function send_data() {
        $(".relate-save-button").addClass('disabled');
        $('#srt_prgrs').html(
            '<img src="/static/images/busy.gif" %}" alt="Busy indicator">'
        ).show();
        chg_data = [];
        $('#fileupload > table > tbody > tr').each(function () {
            chg_data.push($(this).data('order'));
        });

        if (chg_data.length > 0) {
            jqxhr = $.ajax({
                method: "POST",
                url: $('#ord-form').attr("action"),
                data: $('#ord-form').serialize() + "&chg_data=" + JSON.stringify(chg_data)
            })
                .done(function (response) {
                    console.log("ok");
                    $('#fileupload > table > tbody > tr').each(function () {
                        $(this).data('order').new_ord = $(this).data('order').old_ord;
                        $('[class*=btn-srt]').removeClass('disabled');
                        $(".relate-save-button").removeClass('disabled');
                    });
                    $('#srt_prgrs').html(response.message);
                    $('#fileupload').trigger("order_changed");
                    window.setTimeout(function () {
                        $('#srt_prgrs').fadeOut();
                    }, 3000);
                })
                .fail(function (response) {
                    console.log(response);
                    $('#srt_prgrs').html(gettext('Failed!') + " " + response.responseJSON.message);
                    window.setTimeout(function () {
                        $('#srt_prgrs').fadeOut();
                    }, 3000);
                });
            return false;
        } else {
            $('#fileupload > table > tbody > tr').each(function () {
                console.log("unchanged??");
                $(this).data('order').new_ord = $(this).data('order').old_ord;
                $('[class*=btn-srt]').removeClass('disabled');
                $(".relate-save-button").removeClass('disabled');
            });
        }

    }

    $up = $(".up");
    $up.click(function () {
        $('[class*=btn-srt]').addClass('disabled');
        var $tr = $(this).parents("tr");
        if ($tr.index() !== 0) {
            row1 = $tr;
            row2 = $tr.prev();
            $tr.prev().before($tr);
            $up = $(".up");
            assignOrder();
            send_data();

        }
    });
    $down = $(".down");
    len = $down.length;
    $down.click(function () {
        $('[class*=btn-srt]').addClass('disabled');
        var $tr = $(this).parents("tr");
        if ($tr.index() !== len - 1) {
            $tr.next().after($tr);
            $down = $(".down");
            assignOrder();
            send_data();
        }
    });
    $top = $(".top");
    $top.click(function () {
        $('[class*=btn-srt]').addClass('disabled');
        var $tr = $(this).parents("tr");
        if ($tr.index() !== 0 && $tr.index() !== 1) {
            $(".table").prepend($tr);
            $tr.css("color", "#f60");
            $top = $(".top");
            assignOrder();
            send_data();
        }
    });
});

$('.btn-srt-tbl-cfm').on('click', function () {
    'use strict';
    $(this).addClass('hidden');
    $('.btn-srt-tbl').removeClass('hidden');
    $('.td-dl').each(function () {
        $(this).removeClass('hidden');
    });

    $('.td-srt').each(function () {
        $(this).addClass('hidden');
    });
    $('#fileupload > .fileupload-buttonbar > div > *').not('.btn-srt-tbl-cfm').not('.btn-srt-tbl').removeClass('disabled');
});

var clicked_row;
var target_image_pk;
$('#fileupload').on("click", ".btn-edit-image", function () {
    'use strict';
    target_image_pk = $(event.target).closest('tr').attr('data-file-pk');
});

// close gallery using back button
$('#blueimp-gallery').on('open', function (e) {
    if(getWidthQueryMatch()){window.history.pushState('forward', null, '#slides');}
})
    .on('close', function (e) {
        if(location.hash=='#slides' && getWidthQueryMatch())window.history.back();
});


var all_pks;

// http://stackoverflow.com/a/8645155/3437454
// function loadImage(src)

window.addEventListener('DOMContentLoaded', function () {
    'use strict';
    $('.modal .modal-body')
        .css('overflow-y', 'auto')
        .css('max-height', $(window).height() * 0.9)
        .css('margin', 0).css('border', 0);
    var $image, contData, result;
    $('body').on('shown.bs.modal', function () {
        $(".relate-save-button").addClass('disabled');
        var image = new Image();
        $image = $("#image");
        $(image).on('load', function() {
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
                    console.log("cropper ready!");
                    // $('.btn-crp-rtt').removeClass("disabled");
                    // $('.btn-crp-preview').removeClass("disabled");
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
        });

        image.src = $image.attr("src");

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

            $image.cropper('rotate',angle);

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

        $(".btn-crp-rtt").click(function () {
            rtt($(this).data("step"));
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
            var x, y, width, height, rotate, jqxhr, msg;
            $(this).addClass("disabled");
            $(".modal-footer > button").addClass("disabled");
            jqxhr = $.ajax({
                method: "POST",
                url: $image.attr("data-ajax-url"),
                data: JSON.stringify(result, ['x', 'y', 'height', 'width', 'rotate']),
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", get_cookie('csrftoken'));
                }
            })
                .done(function (response) {
                    var new_img = response.file;
                    if (window.location.pathname.indexOf("/grading/") === -1) {
                        $("#thumbnail" + target_image_pk).prop("id", "thumbnail" + new_img.pk).removeClass("hidden").prop('src', new_img.thumbnailUrl);
                    } else {
                        $("#thumbnail" + target_image_pk).prop("id", "thumbnail" + new_img.pk).prop('src', new_img.url).prop('style', "width:40vw");
                    }
                    $("#thumbnail" + new_img.pk).parents("span").addClass("processing");
                    $("#previewid" + target_image_pk).prop("id", "previewid" + new_img.pk).prop('href', new_img.url);
                    $("#filename" + target_image_pk).prop("id", "filename" + new_img.pk).prop('href', new_img.url);
                    $("#filetime" + target_image_pk).prop("id", "filetime" + new_img.pk).prop('title', new_img.timestr_title).html(new_img.timestr_short);
                    $("#filesize" + target_image_pk).prop("id", "filesize" + new_img.pk).html(formatFileSize(new_img.size));
                    $("#updateurl" + target_image_pk).prop("id", "updateurl" + new_img.pk).prop('href', new_img.updateUrl);
                    $("#deleteurl" + target_image_pk).prop("id", "deleteurl" + new_img.pk).prop('href', new_img.deleteUrl);
                    $image.cropper('replace', new_img.url);
                    crpMsg(true, gettext('Done!'));
                    setTimeout(function () {
                        $('#editPopup').modal('hide');
                    }, 2000);
                    $('#fileupload').trigger("file_edited");
                })
                .fail(function (response) {
                    msg = gettext('Failed!') + " " + response.responseJSON.message;
                    crpMsg(false, msg);
                    //console.log(response);
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
        .on('hidden.bs.modal', '.modal', function () {
            $(".relate-save-button").removeClass('disabled');
            $('.img-container').html("");
            $(this).removeData('bs.modal');
            $image.cropper('destroy');
            // window.history.back();
        });

    // Enable back button to close modal and blueimp gallery
    // http://stackoverflow.com/a/40364619/3437454
    $('#editPopup').on('show.bs.modal', function (e) {
        if(getWidthQueryMatch())window.history.pushState('forward', null, '#edit');
    })
        .on('hide.bs.modal', function (e) {
            if(location.hash=='#edit' && getWidthQueryMatch())window.history.back();
        });

    $(window).on('popstate', function (event) {  //pressed back button
        if(event.state!==null && getWidthQueryMatch())
        {
            var gallery = $('#blueimp-gallery').data('gallery');
            if(gallery){gallery.close();}
            else{
                $('.modal').modal('hide');
                console.log("called!");
            }
        }
    });
});


function activate_change_listening() {
    var input_changed = false;
    function pk_changed(evt) {
        all_pks = [];
        $("#img-presentation-table").find('[id*=thumbnail]').each(function(){ all_pks.push(this.id.replace("thumbnail","")); });
        $("#id_hidden_answer").prop("value", all_pks);
    }

    function on_input_change(evt) {
        input_changed = true;
    }

    $(":file").on("change", on_input_change);

    $(window).on('beforeunload',
        function() {
            if (input_changed)
                return "{% trans 'You have unsaved changes on this page.' %}";
        });

    $('#fileupload')
        .on("fileuploadloadingexistalways", function() {
            $(".fileupload-download-processing").remove();})
        .on("file_edited order_changed fileuploaddestroyed", on_input_change)
        .on("file_edited fileuploadcompleted order_changed fileuploaddestroyed", pk_changed)
        .on("fileuploadcompleted fileuploaddestroyed", function () {
            if ($('.timestr').length > 1) {
                if ($(".btn-srt-tbl-cfm").hasClass("hidden")) {
                    $(".btn-srt-tbl").removeClass("hidden");
                }
            } else {
                $(".btn-srt-tbl").addClass("hidden");
            }
        })
        .on("fileuploadadd", function (e, data) {
            disable_submit_button(true);
            console.log(data);
            // debug_files=data;

        })
        .on("fileuploadfailed fileuploadcompleted fileuploaddestroyed", function () {
            var nInProcess = $("#img-presentation-table").find("button.btn.btn-warning.cancel").length;
            disable_submit_button(nInProcess > 0);
        })
        .on('fileuploadprocessstart', function () {
            console.log('processstart');
        })
        .on('fileuploadprocessdone', function (e, data) {
            console.log('processdone', data.files[data.index].name);
            debug_data = data;
            debug_files = data.files[data.index];
        });

    function before_submit(evt) {
        input_changed = false;

        // We can't simply set "disabled" on the submitting button here.
        // Otherwise the browser will simply remove that button from the POST
        // data.

        $(".relate-save-button").each(
            function()
            {
                var clone = $(this).clone();
                $(clone).attr("disabled", "1");
                $(this).after(clone);
                $(this).hide();
            });
    }

    $(".relate-interaction-container form").on("submit", before_submit);
}

$(document).ready(activate_change_listening);