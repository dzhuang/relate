(function ($, window, document, undefined) {
    'use strict';

    $.widget(
        'blueimp.fileupload', $.blueimp.fileupload, {

            options: {
                EditModalSelector: "#editModal",
                EditModalImgSelector: "#image",
                cropResultMessageBoxSelector: "#crp-result",
                cropControlButtonDivSelector: ".cropper-btns",

                added: function (e, data) {
                    var $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload'),
                        options = that.options;
                    if (data.replaceChild && data.replaceChild.length) {
                        var $modal = $(options.EditModalSelector);
                        $(data.context).replaceAll(data.replaceChild);
                        that._trigger("replaced", e, data);
                    }
                    if (!data.files) {
                        return;
                    }
                    var orig, mod = data.files[0];
                    $.each(data.originalFiles, function (i, v) {
                        if (v.name === mod.name) {
                            orig = v;
                            return true;
                        }
                    });
                    if (!orig) {
                        return;
                    }
                    $(data.context).find('.edit').prop('disabled', false);
                }
            },

            _initEventHandlers: function () {
                this._super();
                this._on(this.options.filesContainer, {
                    'click .edit': this._editHandler
                });
            },

            _editHandler: function (e) {
                e.preventDefault();

                var $button = $(e.currentTarget),
                    options = this.options,
                    $fileupload = this.element,
                    template = $button.closest('.template-upload,.template-download'),
                    editType = template.hasClass("template-download") ? "download" : "upload",
                    $editModal = $(options.EditModalSelector),
                    $editImg = $(options.EditModalImgSelector);

                if (editType === "upload") {
                    var data = template.data("data");
                    if (!data) {
                        $button.prop("disabled", true);
                        return;
                    }
                    var orig, mod = data.files[0];
                    $.each(data.originalFiles, function (i, v) {
                        if (v.name === mod.name) {
                            orig = v;
                            return true;
                        }
                    });
                    if (!orig) {
                        return;
                    }

                    $editImg.prop('src', loadImage.createObjectURL(orig));
                    $editImg.processCroppedCanvas = function (result) {
                        var messageBox = $(options.cropResultMessageBoxSelector);
                        $editModal.modal('hide');
                        $fileupload.find(options.cropControlButtonDivSelector + " .btn").prop("disabled", true);
                        result.toBlob(function (blob) {
                            blob.name = mod.name;
                            $fileupload.fileupload(
                                'option', {"maxNumberOfFiles": options.maxNumberOfFiles + 1});
                            $fileupload.fileupload(
                                'add', {
                                    files: [blob],
                                    replaceChild: $(data.context)
                                }
                            );
                            $fileupload.fileupload(
                                'option', {"maxNumberOfFiles": options.maxNumberOfFiles - 1});
                        }, orig.type);
                    };
                }

                if (editType === "download") {
                    $editImg.attr('src', $button.data("src"));
                    $editImg.submitData = function (result) {
                        var messageBox = $(options.cropResultMessageBoxSelector);
                        var jqxhr = $.ajax({
                            method: "POST",
                            url: $button.data("action"),
                            data: JSON.stringify(result),
                            beforeSend: function (xhr, settings) {
                                xhr.setRequestHeader("X-CSRFToken", $button.data("data"));
                            }
                        })
                            .always(function () {
                                window.setTimeout(function () {
                                    messageBox.removeClass().html("");
                                }, 3000);
                                setTimeout(function () {
                                    $editModal.modal('hide');
                                }, 3000);
                            })
                            .done(function (response) {
                                options.done.call($fileupload,
                                    $.Event('done'),
                                    {
                                        result: {files: [response.file]},
                                        context: $button.closest(".template-download")
                                    });
                                messageBox.addClass('alert alert-success').html(response.message);
                            })
                            .fail(function (response) {
                                messageBox.addClass('alert alert-danger').html(response.responseJSON.message);
                            });
                        return false;
                    };
                }

                $editImg.rotateCanvas = function () {
                    var $this = $(this);
                    var contData = $this.cropper('getContainerData');
                    var canvData = $this.cropper('getCanvasData');
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
                        newCanvData = {
                            height: contData.height,
                            width: newWidth,
                            top: 0,
                            left: (contData.width - newWidth) / 2
                        };
                    }
                    $this.cropper('setCanvasData', newCanvData);
                    $this.cropper('setCropBoxData', newCanvData);
                    $fileupload.find(options.cropControlButtonDivSelector + " .btn").prop("disabled", false);
                };

                $editModal.modal('show', [$editImg, editType]);
            }

        }
    );
})(jQuery, window, document);

$(function () {
    "use strict";
    var $image;
    var editType;
    var $editModal = $('#editModal');

    $editModal
        .on('show.bs.modal', function (e) {
            $image = e.relatedTarget[0];
            editType = e.relatedTarget[1];
            $(this).find('.modal-body').css({
                width: 'auto', //probably not needed
                height: 'auto', //probably not needed
                'max-height': '100%'
            });
        })
        .on('shown.bs.modal', function () {
            $(".relate-save-button").addClass('disabled');
            $image.cropper({
                viewMode: 1,
                checkOrientation: false,
                autoCrop: true,
                autoCropArea: 1,
                strict: true,
                movable: false,
                zoomable: false,
                minContainerheight: $(window).height() * 0.8,
                ready: function (e) {
                    $editModal.find(".cropper-rotate-btns .btn").prop("disabled", false);
                },
                cropstart: function (e) {
                },
                crop: function (e) {
                },
                cropend: function (e) {
                    $editModal.find('.cropper-status-btns .btn').prop("disabled", false);
                }
            });

        })
        .on('hidden.bs.modal', function () {
            $(".relate-save-button").removeClass('disabled');

            $image.cropper('destroy');
            $(this)
                .find('.cropper-btns .btn').prop("disabled", true)
                .end();
        })
        .on('show.bs.modal', function (e) {
            // Enable back button to close modal and blueimp gallery
            // http://stackoverflow.com/a/40364619/3437454
            if (getWidthQueryMatch_md_sm_xs())
                window.history.pushState('forward', null, '#edit');
        })
        .on('hide.bs.modal', function (e) {
            if (location.hash === '#edit' && getWidthQueryMatch_md_sm_xs())
                window.history.back();
        });

    $editModal.find('.cropper-btns').on(
        'click',
        '[data-method]',
        function () {
            var data = $.extend({}, $(this).data()); // Clone
            if (data.method === "rotate") {
                var contData = $image.cropper('getContainerData');
                $image.cropper('setCropBoxData', {
                    width: 2,
                    height: 2,
                    top: (contData.height / 2) - 1,
                    left: (contData.width / 2) - 1
                });
                contData = null;
            }
            else if (data.method === "commit") {
                if (editType === "download") {
                    data.method = "getData";
                }
                else if (editType === "upload") {
                    data.method = "getCroppedCanvas";
                }
            }

            var result = $image.cropper(data.method, data.option,
                data.secondOption);

            switch (data.method) {
                case 'scaleX':
                case 'scaleY':
                    $(this).data('option', -data.option);
                    break;
                case 'reset':
                    $editModal.find('.cropper-status-btns .btn').prop("disabled", true);
                    break;
                case 'getData':
                    if (result && $image.submitData) {
                        $image.submitData(result);
                    }
                    break;
                case 'getCroppedCanvas':
                    if (result && $image.processCroppedCanvas) {
                        $image.processCroppedCanvas(result);
                    }
                    break;
                case 'rotate':
                    if (result && $image.rotateCanvas) {
                        $image.rotateCanvas();
                    }
                    break;
            }
        });

});

function get_all_pks(that) {
    var all_pks = [];
    $(that).fileupload("option", "filesContainer")
        .children().not('.processing')
        .each(function () {
            all_pks.push($(this).attr("data-file-pk"));
        });
    return all_pks;
}

function disable_submit_button(bool) {
    $(".relate-save-button").prop("disabled", bool);
}

function hide_fileupload_control_button(that, bool) {
    $(that).find('.fileupload-buttonbar')
        .find('.start, .cancel')
        .css("display", bool ? "none" : "")
        .prop("disabled", bool);
}

function hide_fileupload_sortable_handle(that) {
    if ($(that).fileupload("option", "filesContainer")
            .children().length > 1) {
        $(that).find('.imageSortableHandle').removeClass("hidden");
    } else {
        $(that).find('.imageSortableHandle').addClass("hidden");
    }
}

function toggle_fileupload_control_delete(that) {
    var buttonBar = $(that).find('.fileupload-buttonbar'),
        deletebutton = buttonBar.find('.delete'),
        toggle = buttonBar.find(".toggle"),
        disabledBool = $(that).find(".toggle:checked").length === 0,
        displayBool = !$(that).fileupload("option", "filesContainer").children()
            .not('.processing').length;
    $(deletebutton).css("display", displayBool ? "none" : "").prop("disabled", disabledBool);
    $(toggle).css("display", displayBool ? "none" : "");
}

function disable_fileupload_control_delete_toggle(bool, that) {
    $(that).find(".fileupload-buttonbar").find(".toggle").prop("disabled", bool);
}

function getWidthQueryMatch_md_sm_xs() {
    return window.matchMedia("(max-width: 1023px)").matches;
}


// close gallery using back button
$('#blueimp-gallery')
    .on('open', function (e) {
        if (getWidthQueryMatch_md_sm_xs()) {
            window.history.pushState('forward', null, '#slides');
        }
    })
    .on('close', function (e) {
        if (location.hash == '#slides'
            &&
            getWidthQueryMatch_md_sm_xs())
            window.history.back();
    });

$(window).on('popstate', function (event) {  //pressed back button
    if (event.state !== null && getWidthQueryMatch_md_sm_xs()) {
        var gallery = $('#blueimp-gallery').data('gallery');
        if (gallery) {
            gallery.close();
        }
        else {
            $('.modal').modal('hide');
        }
    }
});

function activate_change_listening() {
    var input_changed = false;
    var $fileupload = $("#fileupload");

    $fileupload.fileupload("option", "filesContainer")
        .sortable({
            delay: 500,
            handle: ".imageSortableHandle",
            scrollSpeed: 40,
            helper: "clone",
            axis: "y",
            opacity: 0.9,
            cursor: "move",
            stop: function (e, ui) {
                if (window.location.pathname.indexOf("/grading/") === -1) {
                    on_input_change(e, get_all_pks($fileupload));
                }
            }
        });

    var starting_pk;
    var sortableChangeCausal = true;

    function on_input_change(evt, data) {
        if (!sortableChangeCausal) {
            input_changed = true;
            return
        }
        if (!data || evt.type !== "sortstop") {
            input_changed = true;

            // Only change by sortable can be reverted.
            sortableChangeCausal = false;
            return
        }
        input_changed = JSON.stringify(data) !== JSON.stringify(starting_pk);
    }

    $(window).on('beforeunload',
        function () {
            if (input_changed)
                return gettext('You have unsaved changes on this page.');
        });

    $fileupload
        .on("fileuploadadd", function (e, data) {
            disable_submit_button(true);
            hide_fileupload_control_button($(this), false);
        })
        .on("fileuploadadded", function (e, data) {
            on_input_change();
            hide_fileupload_sortable_handle($(this));
        })
        .on("fileuploadcompleted fileuploaddestroyed", function () {
            var n_downloadPk = get_all_pks($(this)).length;
            disable_fileupload_control_delete_toggle(!n_downloadPk, $(this));
            toggle_fileupload_control_delete($(this));
            if (!starting_pk) {
                starting_pk = get_all_pks($fileupload);
            }
            else {
                on_input_change();
            }
        })
        .on("fileuploadfailed fileuploadcompleted fileuploaddestroyed", function () {
            var queue_length = $(this).find('.template-upload').length;
            disable_submit_button(queue_length > 0);
            hide_fileupload_control_button($(this), !queue_length);
            hide_fileupload_sortable_handle($(this));
        })
        .on("fileuploadreplaced", function (e, data) {
            hide_fileupload_sortable_handle($(this));
        });

    $('body').on('change', '#fileupload input[type="checkbox"]', function (e) {
        toggle_fileupload_control_delete($fileupload);
    });

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

$(document).ready(function () {
    'use strict';
    $(".relate-save-button").each(function () {
        $(this)
            .attr("formaction", window.location.pathname)
            .detach()
            .appendTo('#actual-submit-div');
    }).on("click", function () {
        $("#div_id_hidden_answer")
            .html('<div class="controls"/>')
            .find("div")
            .html('<input type="hidden" id="id_hidden_answer" name="hidden_answer" type="text"/>')
            .find("input")
            .prop("value", get_all_pks($("#fileupload")));
    });
});
