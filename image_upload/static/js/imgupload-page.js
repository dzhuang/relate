/*global $, Cropper, gettext, console */

// don't show past submission as those currently won't be saved in page-visit.
$(document).ready(function () {
    //"save", "save_and_next", "save_and_finish", "submit"
    'use strict';
    $(".relate-save-button").each(function () {
        $(this).attr("formaction", window.location.pathname);
    });
    $('#past-submission_dropdown').addClass('hidden');
});


function assignOrder() {
    'use strict';
    var idx = 0;
    $('#fileupload > table > tbody > tr').each(function () {
        $(this).data("order").new_ord = idx;
        idx = idx + 1;
    });
    $('.up').each(function () {$(this).removeClass("hidden"); });
    $('.down').each(function () {$(this).removeClass("hidden"); });
    $('.top').each(function () {$(this).removeClass("hidden"); });
    $('tr:nth-child(1) > td.td-srt > a.button.btn.btn-success.up').addClass("hidden");
    $('tr:nth-child(1) > td.td-srt > a.button.btn.btn-success.top').addClass("hidden");
    $('tr:nth-child(2) > td.td-srt > a.button.btn.btn-success.top').addClass("hidden");
    $('tr:nth-last-child(1) > td.td-srt > a.button.btn.btn-success.down').addClass("hidden");
}


$('.btn-srt-tbl').on('click', function () {
    'use strict';
    var $up, $down, len, row1, row2, $top, chg_data;
    $(this).addClass('hidden');
    $('.btn-srt-tbl-cfm').removeClass('hidden');
    $('.td-dl').each(function () {
        $(this).addClass('hidden');
    });
    $('.td-srt').each(function () {
        $(this).removeClass('hidden');
    });

    assignOrder();
    
    function send_data() {
        chg_data = [];
        $('#fileupload > table > tbody > tr').each(function () {
            if ($(this).data('order').new_ord !== $(this).data('order').old_ord) {
                chg_data.push($(this).data('order'));
            }
        });
        
    }

    //上移 
    $up = $(".up");
    $up.click(function () {
        var indexes = [],
            $tr = $(this).parents("tr");
        if ($tr.index() !== 0) {
            row1 = $tr;
            row2 = $tr.prev();
            $tr.prev().before($tr);
            $up = $(".up");
            assignOrder();
            send_data();

        }
    });
    //下移 
    $down = $(".down");
    len = $down.length;
    $down.click(function () {
        var $tr = $(this).parents("tr");
        if ($tr.index() !== len - 1) {
            //$tr.fadeOut("slow").fadeIn("slow");
            $tr.next().after($tr);
            $down = $(".down");
            assignOrder();
            send_data();
        }
    });
    //置顶 
    $top = $(".top");
    $top.click(function () {
        var $tr = $(this).parents("tr");
        if ($tr.index() !== 0 && $tr.index() !== 1) {
            //$tr.fadeOut().fadeIn();
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
});

var clicked_row;
$('#fileupload').on("click", ".btn-edit-image", function () {
    'use strict';
    clicked_row = $(event.target).closest('tr');
});

window.addEventListener('DOMContentLoaded', function () {
    'use strict';
    $('.modal .modal-body')
        .css('overflow-y', 'auto')
        .css('max-height', $(window).height() * 0.9)
        .css('margin', 0).css('border', 0);
    var cropper, image, dataX, dataY, dataHeight, dataWidth, dataRotate;
    $('body').on('shown.bs.modal', function () {
        image = document.querySelector("#image");
        dataX = document.getElementById('dataX');
        dataY = document.getElementById('dataY');
        dataHeight = document.getElementById('dataHeight');
        dataWidth = document.getElementById('dataWidth');
        dataRotate = document.getElementById('dataRotate');
        $('.img-container img').css('max-height', $(window).height() * 0.8);
        cropper = new Cropper(image, {
            checkOrientation: false,
            autoCrop: true,
            autoCropArea: 1,
            strict: true,
            movable: false,
            zoomable: false,
            minContainerheight: $(window).height() * 0.8,
            cropstart: function (data) {
                $('.btn-crp-submit').removeClass("disabled");
                $('.btn-crp-reset').removeClass("disabled");
            },
            crop: function (data) {
                dataX.value = Math.round(data.x);
                dataY.value = Math.round(data.y);
                dataHeight.value = Math.round(data.height);
                dataWidth.value = Math.round(data.width);
                dataRotate.value = typeof data.rotate === 'undefined' ? data.rotate : '';
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
            var contData, canvData, newWidth, newHeight, newCanvData;
            contData = cropper.getContainerData();

            cropper.setCropBoxData({
                width: 2,
                height: 2,
                top: (contData.height / 2) - 1,
                left: (contData.width / 2) - 1
            });

            cropper.rotate(angle);

            canvData = cropper.getCanvasData();
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

            cropper.setCanvasData(newCanvData)
                .setCropBoxData(newCanvData);

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
                result = cropper.getCroppedCanvas();
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
            x = $('#dataX').val();
            y = $('#dataY').val();
            width = $('#dataWidth').val();
            height = $('#dataHeight').val();
            rotate = $('#dataRotate').val();

            if (x === "" || y === "" || width === "" || height === "" || rotate === "") {
                $(this).removeClass("disabled");
                return false;
            }

            jqxhr = $.ajax({
                method: "POST",
                url: $('#crp-form').attr("action"),
                data: $('#crp-form').serialize()
            })
                .done(function (response) {
                    var new_img = response.file;
                    $("#thumbnail" + new_img.pk).prop('src', new_img.thumbnailUrl);
                    $("#previewid" + new_img.pk).prop('href', new_img.url);
                    $("#filename" + new_img.pk).prop('href', new_img.url);
                    $("#filetime" + new_img.pk).prop('title', new_img.timestr_title).html(new_img.timestr_short);
                    $("#filesize" + new_img.pk).html(formatFileSize(new_img.size));
                    cropper.replace(new_img.url);
                    crpMsg(true, gettext('Done!'));
                    setTimeout(function () {
                        $('#modal').modal('hide');
                    }, 2000);
                })
                .fail(function (response) {
                    msg = gettext('Failed!') + " " + response.responseJSON.message;
                    crpMsg(false, msg);
                    //console.log(response);
                    setTimeout(function () {
                        $('#modal').modal('hide');
                    }, 2000);
                });
            return false;
        });

        $('.btn-crp-reset').click(function () {
            cropper.reset();
            $('.btn-crp-submit').addClass("disabled");
            $('.btn-crp-reset').addClass("disabled");
        });

    });
    $('body').on('hidden.bs.modal', '.modal', function () {
        $('.img-container').html("");
        $(this).removeData('bs.modal');
        cropper.destroy();

    });

});
