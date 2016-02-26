// don't show past submission as those currently won't be saved in page-visit.
$('#past-submission_dropdown').addClass('hidden');

$(document).ready(function () {
    //"save", "save_and_next", "save_and_finish", "submit"
    $(".relate-save-button").each(function () {
        $(this).attr("formaction", window.location.pathname);
    });
});

function assignOrder(){
    var idx= 1; 
    $('#fileupload > table > tbody > tr').each(function(){
    $(this).data("order").order=idx;
    idx=idx+1;
    });
}

$('.sort-table').on('click', function () {
    $(this).addClass('hidden');
    $('.sort-table-submit').removeClass('hidden');
    $('.downloadtd').each(function () {
        $(this).addClass('hidden')
    });
    $('.sorttd').each(function () {
        $(this).removeClass('hidden')
    });
    
    assignOrder();

    //上移 
    var $up = $(".up")
    $up.click(function () {
        var indexes = Array();
        var $tr = $(this).parents("tr");
        if ($tr.index() != 0) {
            $tr.fadeOut("slow").fadeIn("slow");
            var row1 = $tr;
            var row2 = $tr.prev();
//            console.log(row1.data("order"));
//            console.log(row2.data("order"));
            $tr.prev().before($tr);
            $up = $(".up");
            assignOrder();
//            console.log(row1.data("order"));
//            console.log(row2.data("order"));
            indexes.push (row1.data("order"), row1.data("order"));
//            console.log(indexes);
            
        }
    });
    //下移 
    var $down = $(".down");
    var len = $down.length;
    $down.click(function () {
        var $tr = $(this).parents("tr");
        if ($tr.index() != len - 1) {
            //$tr.fadeOut("slow").fadeIn("slow");
            $tr.next().after($tr);
            $down = $(".down");
            assignOrder();
        }
    });
//    //置顶 
//    var $top = $(".top");
//    $top.click(function () {
//        var $tr = $(this).parents("tr");
//        $tr.fadeOut().fadeIn();
//        $(".table").prepend($tr);
//        $tr.css("color", "#f60");
//        $top = $(".top");
//    });
});
$('.sort-table-submit').on('click', function () {
    $(this).addClass('hidden');
    $('.sort-table').removeClass('hidden');
    $('.downloadtd').each(function () {
        $(this).removeClass('hidden')
    });

    $('.sorttd').each(function () {
        $(this).addClass('hidden')
    });
});

//$("tbody").sortable({
//    items: "> tr",
//    appendTo: "parent",
//    helper: "clone"
//}).disableSelection();
//
//$("#tabs ul li a").droppable({
//    hoverClass: "drophover",
//    tolerance: "pointer",
//    drop: function (e, ui) {
//        var tabdiv = $(this).attr("href");
//        $(tabdiv + " table tr:last").after("<tr>" + ui.draggable.html() + "</tr>");
//        ui.draggable.remove();
//    }
//});

var clicked_row;
$('#fileupload').on("click", ".btn-edit-image", function () {
    clicked_row = $(event.target).closest('tr');
});

var cropper;
$('body').on('loaded.bs.modal', function () {
    $('.img-container img').css('max-height', $(window).height() * 0.8);
    var dataX = document.getElementById('dataX');
    var dataY = document.getElementById('dataY');
    var dataHeight = document.getElementById('dataHeight');
    var dataWidth = document.getElementById('dataWidth');
    var dataRotate = document.getElementById('dataRotate');
    var options = {
        checkOrientation: false,

        autoCrop: true,
        autoCropArea: 1,
        strict: true,
        movable: false,
        zoomable: false,
        minContainerheight: $(window).height() * 0.8,
        built: function () {},
        cropstart: function (data) {
            $('#imageCropSubmit').removeClass("disabled");
            $('#imageCropReset').removeClass("disabled");
        },
        crop: function (data) {
            dataX.value = Math.round(data.x);
            dataY.value = Math.round(data.y);
            dataHeight.value = Math.round(data.height);
            dataWidth.value = Math.round(data.width);
            dataRotate.value = !isUndefined(data.rotate) ? data.rotate : '';
        },
    }
    var cropBoxData;
    var canvasData;
    var image = document.querySelector("#image");
    cropper = new Cropper(image, options);

    $('.modal .modal-body')
        .css('overflow-y', 'auto')
        .css('max-height', $(window).height() * 0.9)
        .css('margin', 0).css('border', 0);

    $('#rotate_right').click(function () {
        rotatedegree(90)
    });
    $('#rotate_left').click(function () {
        rotatedegree(-90)
    });
    $('#rotate_mright').click(function () {
        rotatedegree(0.5)
    });
    $('#rotate_mleft').click(function () {
        rotatedegree(-0.5)
    });

    $('#cropper_preview').click(function () {
        var toggle = $('.cropper-container').hasClass("hidden");
        if (!toggle) {
            var result = cropper.getCroppedCanvas();
            $('.cropper-container').addClass("hidden");
            $('#preview').removeClass("hidden").html(result);
            $(this).html("<i class='fa fa-pencil'></i> <span>" + gettext('Edit') + "</span>");
            $("button[id^='rotate_']").addClass("hidden");
            $("#imageCropReset").addClass("hidden");
        } else {
            $('.cropper-container').removeClass("hidden");
            $('#preview').addClass("hidden").html("");
            $(this).html("<i class='fa fa-eye'></i> <span>" + gettext('Preview') + "</span>");
            $("button[id^='rotate_']").removeClass("hidden");
            $("#imageCropReset").removeClass("hidden");
        }
    });

    $('#imageCropSubmit').click(function () {
        $(this).addClass("disabled");
        $(".modal-footer > button").addClass("disabled");
        x = $('#dataX').val();
        y = $('#dataY').val();
        width = $('#dataWidth').val();
        height = $('#dataHeight').val();
        rotate = $('#dataRotate').val();

        if (x === "" || y === "" || width === "" || height === "" || rotate == "") {
            $(this).removeClass("disabled");
            return false;
        }

        var jqxhr = $.ajax({
                method: "POST",
                url: $('#imageCropForm').attr("action"),
                data: $('#imageCropForm').serialize(),
            })
            .done(function (response) {
                var new_img = response.file
                $("#thumbnail" + new_img.pk).prop('src', new_img.thumbnailUrl);
                $("#previewid" + new_img.pk).prop('href', new_img.url);
                $("#filename" + new_img.pk).prop('href', new_img.url);
                $("#filetime" + new_img.pk).prop('title', new_img.timestr_title).html(new_img.timestr_short);
                $("#filesize" + new_img.pk).html(formatFileSize(new_img.size));
                cropper.replace(new_img.url);
                crop_msg(true, gettext('Done!'));
                setTimeout(function () {
                    $('#modal').modal('hide');
                }, 2000);
            })
            .fail(function (response) {
                msg = gettext('Failed!') + " " + response.responseJSON.message
                crop_msg(false, msg);
                console.log(response);
                setTimeout(function () {
                    $('#modal').modal('hide');
                }, 2000);
            });
        return false;
    });

    $('#imageCropReset').click(function () {
        cropper.reset();
        $('#imageCropSubmit').addClass("disabled");
        $('#imageCropReset').addClass("disabled");
    });

}).on('hidden.bs.modal', '.modal', function () {
    $('.img-container').html("");
    $(this).removeData('bs.modal');
    cropper.destroy();

});

function isUndefined(obj) {
    return typeof obj === 'undefined';
}

function crop_msg(success, msg) {
    var e = $("#CropResult");
    if (success === true) {
        e.addClass('alert alert-success').html(msg);
    } else {
        console.log(success)
        e.addClass('alert alert-danger').html(msg);
    }
    window.setTimeout(
        function () {
            e.removeClass().html("");
        },
        3000);
}

function rotatedegree(angle) {
    var contData = cropper.getContainerData();

    cropper.setCropBoxData({
        width: 2,
        height: 2,
        top: (contData.height / 2) - 1,
        left: (contData.width / 2) - 1
    });

    cropper.rotate(angle);

    var canvData = cropper.getCanvasData();
    var newWidth = canvData.width * (contData.height / canvData.height);

    if (newWidth >= contData.width) {
        var newHeight = canvData.height * (contData.width / canvData.width);
        var newCanvData = {
            height: newHeight,
            width: contData.width,
            top: (contData.height - newHeight) / 2,
            left: 0
        };
    } else {
        var newCanvData = {
            height: contData.height,
            width: newWidth,
            top: 0,
            left: (contData.width - newWidth) / 2
        };
    }

    cropper.setCanvasData(newCanvData);
    cropper.setCropBoxData(newCanvData);

    $('#imageCropSubmit').removeClass("disabled");
    $('#imageCropReset').removeClass("disabled");
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