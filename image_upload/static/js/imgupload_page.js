    $("tbody").sortable({
        items: "> tr",
        appendTo: "parent",
        helper: "clone"
    }).disableSelection();

    $("#tabs ul li a").droppable({
        hoverClass: "drophover",
        tolerance: "pointer",
        drop: function (e, ui) {
            var tabdiv = $(this).attr("href");
            $(tabdiv + " table tr:last").after("<tr>" + ui.draggable.html() + "</tr>");
            ui.draggable.remove();
        }
    });
    var clicked_row;
    var clicked_response;
    $('#fileupload').on("click", ".btn-edit-image", function(){
        clicked_row = $(event.target).closest('tr');
    });
    
    //console.log(clicked_row);
    
    var cropper;
    $('body').on('shown.bs.modal', function () {
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
            built: function () {
            },
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
        var image = document.getElementById("image");
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
                $(this).html("<i class='fa fa-pencil'></i> <span>"+gettext('Edit')+"</span>");
                $("button[id^='rotate_']").addClass("hidden");
                $("#imageCropReset").addClass("hidden");
            } else {
                $('.cropper-container').removeClass("hidden");
                $('#preview').addClass("hidden").html("");
                $(this).html("<i class='fa fa-eye'></i> <span>"+gettext('Preview')+"</span>");
                $("button[id^='rotate_']").removeClass("hidden");
                $("#imageCropReset").removeClass("hidden");
            }
        });

        $('#imageCropSubmit').click(function () {
            $(this).addClass("disabled");
            x = $('#dataX').val();
            y = $('#dataY').val();
            width = $('#dataWidth').val();
            height = $('#dataHeight').val();
            rotate = $('#dataRotate').val();

            if (x === "" || y === "" || width === "" || height === "" || rotate == "")
            {
                $(this).removeClass("disabled");
                return false;
            }
            
             var jqxhr = $.ajax(
                 {
                     method: "POST",
                     url: $('#imageCropForm').attr("action"),
                     data: $('#imageCropForm').serialize(),
                 })
                 .done(function (response) {
//                     $("#thumbnail"+response.file.pk).attr('src',response.file.thumbnailUrl);
//                     var oldsrc = $('#image').attr('src');
//                      $('#image').attr('src', oldsrc + "#" + new Date().getTime());
//                     //$("#filename"+response.file.pk).attr('src', response.file.url + "#" + new Date().getTime());
                     crop_success_msg(gettext('Done!'));
                     setTimeout(function() { $('#modal').modal('hide'); }, 2000);
                     console.log($(response));
                     window.location.reload();

                 })
                 .fail(function () {
                     crop_failed_msg(gettext('Failed!'));
                 });
            
            return false;

        });

        $('#imageCropReset').click(function () {
            cropper.reset();
            $('#imageCropSubmit').addClass("disabled");
            $('#imageCropReset').addClass("disabled");
        });

    }).on('hidden.bs.modal', '.modal', function () {
        $(this).removeData('bs.modal');
        cropper.destroy();
    });

    function isUndefined(obj) {
        return typeof obj === 'undefined';
    }

    function crop_success_msg(msg) {
        $("#CropResult").addClass('alert alert-success').html(msg);
        window.setTimeout(
            function () {
                $("#CropResult").removeClass('alert alert-error').removeClass('alert alert-success').html("");
            },
            3000);
    }
    
    function crop_failed_msg(msg) {
        $("#CropResult").addClass('alert alert-error').html(msg);
        window.setTimeout(
            function () {
                $("#CropResult").removeClass('alert alert-error').removeClass('alert alert-success').html("");
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