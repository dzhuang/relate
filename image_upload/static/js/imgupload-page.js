$(document).ready(function () {
    'use strict';
    $(".relate-save-button").each(function () {
        $(this).attr("formaction", window.location.pathname).detach().appendTo('#real-submit-div');
    });
    // $('#past-submission_dropdown').addClass('hidden');
    new Clipboard('.btn-data-copy');
    var input_changed = false;
});

function watch(targetElement, triggerFunction) {
    'use strict';
    var html = targetElement.innerHTML;
    setInterval(function () {
        if (html !== targetElement.innerHTML) {
            triggerFunction();
            html = targetElement.innerHTML;
        }
    }, 500);
}

function table_changed() {
    'use strict';
    var imgCount = $('.timestr').length;
    if (imgCount > 1) {
        if ($(".btn-srt-tbl-cfm").hasClass("hidden")) {
            $(".btn-srt-tbl").removeClass("hidden");
        }
    } else {
        $(".btn-srt-tbl").addClass("hidden");
    }
}

watch(document.getElementById('img-presentation-table'), table_changed);

function assignOrder() {
    'use strict';
    var idx = 0;
    $('#fileupload > table > tbody > tr').each(function () {
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
var clicked_row_id;
$('#fileupload').on("click", ".btn-edit-image", function () {
    'use strict';
    clicked_row = $(event.target).closest('tr');
    clicked_row_id = $(clicked_row).find('[id*=thumbnail]').prop("id").replace("thumbnail","");
    console.log(clicked_row_id);
});

var all_pks;

window.addEventListener('DOMContentLoaded', function () {
    'use strict';
    $('.modal .modal-body')
        .css('overflow-y', 'auto')
        .css('max-height', $(window).height() * 0.9)
        .css('margin', 0).css('border', 0);
    var cropper, image, dataX, dataY, dataHeight, dataWidth, dataRotate;
    $('body').on('shown.bs.modal', function () {
        $(".relate-save-button").addClass('disabled');
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
                dataRotate.value = Math.round(data.rotate);
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
                    if (window.location.pathname.indexOf("/grading/") === -1) {
                        $("#thumbnail" + clicked_row_id).prop("id", "thumbnail" + new_img.pk).prop('src', new_img.thumbnailUrl);
                    } else {
                        $("#thumbnail" + clicked_row_id).prop("id", "thumbnail" + new_img.pk).prop('src', new_img.url).prop('style', "width:40vw");
                    }
                    $("#previewid" + clicked_row_id).prop("id", "previewid" + new_img.pk).prop('href', new_img.url);
                    $("#filename" + clicked_row_id).prop("id", "filename" + new_img.pk).prop('href', new_img.url);
                    $("#filetime" + clicked_row_id).prop("id", "filetime" + new_img.pk).prop('title', new_img.timestr_title).html(new_img.timestr_short);
                    $("#filesize" + clicked_row_id).prop("id", "filesize" + new_img.pk).html(formatFileSize(new_img.size));
                    $("#updateurl" + clicked_row_id).prop("id", "updateurl" + new_img.pk).prop('href', new_img.updateUrl);
                    $("#deleteurl" + clicked_row_id).prop("id", "deleteurl" + new_img.pk).prop('href', new_img.deleteUrl);
                    cropper.replace(new_img.url);
                    crpMsg(true, gettext('Done!'));
                    setTimeout(function () {
                        $('#modal').modal('hide');
                    }, 2000);
                    $('#fileupload').trigger("file_edited");
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
        $(".relate-save-button").removeClass('disabled');
        $('.img-container').html("");
        $(this).removeData('bs.modal');
        cropper.destroy();

    });

});


function activate_change_listening()
{  var input_changed = false;
  function pk_changed(evt)
    {
        all_pks = [];
        $("#img-presentation-table").find('[id*=thumbnail]').each(function(){ all_pks.push(this.id.replace("thumbnail","")); });
        $("#id_hidden_answer").prop("value", all_pks);
    }

  function on_input_change(evt)
  {
    input_changed = true;
  }

  $(":file").on("change", on_input_change);

  $('#fileupload').on("file_edited order_changed fileuploaddestroyed", on_input_change);
  $('#fileupload').on("file_edited fileuploadcompleted order_changed fileuploaddestroyed", pk_changed);

  $(window).on('beforeunload',
      function()
      {
        if (input_changed)
          return "{% trans 'You have unsaved changes on this page.' %}";
      });

  function before_submit(evt)
  {
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