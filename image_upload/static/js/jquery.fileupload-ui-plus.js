(function ($, window, document, undefined) {
    'use strict';

    $.blueimp.fileupload.prototype._specialOptions.push(
        'editModalId',
        'editModalImgId',
        'sortableHandleSelector',
        'sortableOptions',
        'cropperResultMessageBoxSelector',
        'cropperButtonDivSelector',
        'cropperButtonSelector',
        'statusDataName'
    );

    var originalAdded = $.blueimp.fileupload.prototype.options.added;

    $.widget(
        'blueimp.fileupload', $.blueimp.fileupload, {

            options: {
                editModalId: undefined,
                editModalImgId: undefined,
                cropperResultMessageBoxSelector: undefined,
                cropperButtonDivSelector: undefined,
                cropperStatusBtnSelector: undefined,
                cropperRotateBtnSelector: undefined,
                enableSortable: true,
                sortableHandleSelector: undefined,
                sortableOptions:undefined,
                statusDataName: undefined,

                getNumberOfUploadedFiles: function () {
                    return this.filesContainer.children('.template-download')
                        .not('.processing').length;
                },

                getStatus: function (){
                    var that = this,
                        statusArray = [];
                    this.filesContainer.children()
                        .not('.processing')
                        .each(function () {
                            statusArray.push($(this).data(that.statusDataName));
                        });
                    return statusArray;
                },

                added: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }

                    var $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload');
                    if (!data.files) return false;
                    if (data.replaceChild && data.replaceChild.length){
                        if (that._trigger('replace', e, data) !== false)
                        {delete data.replaceChild;}
                    }
                    $(data.context).find('.edit').prop('disabled', false);
                    if ($.isFunction( originalAdded )){
                        originalAdded.call(this, e, data);
                    }
                    that.toggleFileuploadSortableHandle();
                    that._toggleFileuploadButtonBarButtonDisplay();
                },

                replace: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    var $this = $(this),
                        that = $this.data('blueimp-fileupload') ||
                            $this.data('fileupload'),
                        options = that.options;

                    var $modal = options.editModalId;
                    $(data.context).replaceAll(data.replaceChild);
                },

                completed: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    var that = $(this).data('blueimp-fileupload') || $(this).data('fileupload'),
                        options = that.options;
                    that.toggleFileuploadSortableHandle()
                        ._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                    if ($(this).data.initialStatus === undefined) {
                        $(this).data.initialStatus = options.getStatus();
                    }
                },

                failed: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    var that = $(this).data('blueimp-fileupload') || $(this).data('fileupload');
                    that.toggleFileuploadSortableHandle()
                        ._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                },

                destroyed: function (e, data) {
                    if (e.isDefaultPrevented()) {
                        return false;
                    }
                    var that = $(this).data('blueimp-fileupload') || $(this).data('fileupload');
                    that.toggleFileuploadSortableHandle()
                        ._toggleFileuploadButtonBarButtonDisplay()._toggleFileuploadButtonBarDelete();
                }

            },

            _initEventHandlers: function () {
                this._super();
                var filesContainer = this.options.filesContainer;
                this._on(filesContainer, {
                    'click .edit': this._editHandler
                });
                this._on(this.element, {
                    'change .toggle': this._toggleFileuploadButtonBarDeleteDisable
                });
            },

            _toggleFileuploadButtonBarDeleteDisable: function(e) {
                this.element.find('.fileupload-buttonbar')
                    .find('.delete')
                    .prop(
                        'disabled',
                        !(this.element.find('.toggle').is(':checked'))
                    );
            },

            toggleFileuploadSortableHandle: function() {
                var $this = $(this),
                    options = this.options;
                if (!options.enableSortable) return;

                var filesContainer = options.filesContainer;
                if (filesContainer.children().length > 1) {
                    filesContainer.find(options.sortableHandleSelector).removeClass("hidden").end();
                } else {
                    filesContainer.find(options.sortableHandleSelector).addClass("hidden").end();
                }
                return this;
            },

            _toggleFileuploadButtonBarButtonDisplay: function() {
                var filesContainer = this.options.filesContainer,
                    bool = filesContainer.find('.template-upload').length === 0;
                this.element.find('.fileupload-buttonbar')
                    .find('.start, .cancel')
                    .css("display", bool ? "none" : "")
                    .prop("disabled", bool)
                    .end();
                return this;
            },

            _toggleFileuploadButtonBarDelete: function () {
                var filesContainer = this.options.filesContainer;
                var that = this.element,
                    disabledBool = that.find(".toggle:checked").length === 0,
                    displayBool = !(this.options.getNumberOfUploadedFiles());
                that.find('.fileupload-buttonbar')
                    .find('.delete')
                    .css("display", displayBool ? "none" : "").prop("disabled", disabledBool).end()
                    .find(".toggle")
                    .css("display", displayBool ? "none" : "")
                    .end();
                return this;
            },

            _editHandler: function (e) {
                e.preventDefault();

                var $button = $(e.currentTarget),
                    options = this.options,
                    $fileupload = this.element,
                    template = $button.closest('.template-upload,.template-download'),
                    editType = template.hasClass("template-download") ? "download" : "upload",
                    $editModal = options.editModalId,
                    $editImg = options.editModalImgId;

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
                        $editModal.modal('hide');
                        options.cropperButtonSelector.prop("disabled", true);
                        template.find(".btn").prop("disabled", true);

                        // cheat maxNumberOfFiles count minus 1
                        data.context.addClass('processing');
                        result.toBlob(function (blob) {
                            blob.name = mod.name;
                            $fileupload.fileupload(
                                'add', {
                                    files: [blob],
                                    replaceChild: $(data.context)
                                }
                            );
                        }, orig.type);
                    };
                }

                if (editType === "download") {
                    $editImg.attr('src', $button.data("src"));
                    $editImg.submitData = function (result) {
                        var messageBox = options.cropperResultMessageBoxSelector;
                        options.cropperButtonSelector.prop("disabled", true);
                        $editImg.cropper('disable');
                        var jqxhr = $.ajax({
                            method: "POST",
                            url: $button.data("action"),
                            data: {"croppedResult": JSON.stringify(result)},
                            beforeSend: function (xhr, settings) {
                                xhr.setRequestHeader("X-CSRFToken", $button.data("data"));
                            }
                        })
                            .always(function () {
                            })
                            .done(function (response) {
                                options.done.call($fileupload,
                                    $.Event('done'),
                                    {
                                        result: {files: [response.file]},
                                        context: $button.closest(".template-download")
                                    });
                                messageBox.html("<span class='alert alert-success'>" + response.message +"</span>");
                                $editModal.data("new", false);
                                    setTimeout(function () {
                                        if(!$editModal.data("new")){$editModal.modal('hide')}
                                    }, 3000);
                            })
                            .fail(function (response) {
                                messageBox.html("<span class='alert alert-danger'>" + response.responseJSON.message + "</span>");
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
                    $this.cropper('setCanvasData', newCanvData).cropper('setCropBoxData', newCanvData);
                    options.cropperButtonSelector.prop("disabled", false);
                };

                $editModal.modal('show', [$editImg, editType]);
            },

            _initEditModalId: function () {
                var options = this.options;
                if (options.editModalId === undefined) {
                    options.editModalId = this.element.find("#editModal");
                } else if (!(options.editModalId instanceof $)) {
                    options.editModalId = $(options.editModalId);
                }
            },

            _initEditModalImgId: function () {
                var options = this.options;
                if (options.editModalImgId === undefined) {
                    options.editModalImgId = this.element.find("#modalImage");
                } else if (!(options.editModalImgId instanceof $)) {
                    options.editModalImgId = $(options.editModalImgId);
                }
            },

            _initCropperResultMessageBoxSelector: function () {
                var options = this.options;
                if (options.cropperResultMessageBoxSelector === undefined) {
                    options.cropperResultMessageBoxSelector = this.element.find("#cropper-message");
                } else if (!(options.cropperResultMessageBoxSelector instanceof $)) {
                    options.cropperResultMessageBoxSelector = $(options.cropperResultMessageBoxSelector);
                }
            },

            _initCropperButtonDivSelector: function () {
                var options = this.options;
                if (options.cropperButtonDivSelector === undefined) {
                    options.cropperButtonDivSelector = this.element.find(".cropper-btns");
                } else if (!(options.cropperButtonDivSelector instanceof $)) {
                    options.cropperButtonDivSelector = $(options.cropperButtonDivSelector);
                }
            },

            _initCropperButtonSelector: function () {
                var options = this.options;
                options.cropperButtonSelector = options.cropperButtonDivSelector.find(".btn")
            },

            _initCropperStatusBtnSelector: function () {
                var options = this.options;
                if (options.cropperStatusBtnSelector === undefined) {
                    options.cropperStatusBtnSelector = this.element.find('.cropper-status-btns .btn');
                } else if (!(options.cropperStatusBtnSelector instanceof $)) {
                    options.cropperStatusBtnSelector = $(options.cropperStatusBtnSelector);
                }
            },

            _initCropperRotateBtnSelector: function () {
                var options = this.options;
                if (options.cropperRotateBtnSelector === undefined) {
                    options.cropperRotateBtnSelector = this.element.find(".cropper-rotate-btns .btn");
                } else if (!(options.cropperRotateBtnSelector instanceof $)) {
                    options.cropperRotateBtnSelector = $(options.cropperRotateBtnSelector);
                }
            },

            _initEditModalEventHandler: function(){
                var $editModal = this.options.editModalId,
                    that = this,
                    options = that.options,
                    $image, editType, croppStartingData;
                $editModal.on('show.bs.modal', function (e) {
                    $image = e.relatedTarget[0];
                    editType = e.relatedTarget[1];
                })
                    .on('shown.bs.modal', function () {
                        $(this).data('new', true);
                        that._trigger("modalshownevent", event, true);
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
                                croppStartingData = $image.cropper("getData", "true");
                                options.cropperRotateBtnSelector.prop("disabled", false);
                            },
                            cropstart: function (e) {
                                that._trigger('modalinprogessstatus', event, true);
                            },
                            crop: function (e) {
                            },
                            cropend: function (e) {
                                var currentData = $image.cropper("getData", "true");
                                var cropNotChanged = JSON.stringify(croppStartingData) === JSON.stringify(currentData);
                                options.cropperStatusBtnSelector.prop("disabled", cropNotChanged);
                                that._trigger('modalinprogessstatus', event, !cropNotChanged);
                            }
                        });

                    })
                    .on('hidden.bs.modal', function () {
                        that._trigger('modalinprogessstatus', event, false);
                        that._trigger("modalhiddenevent", event, true);
                        $image.cropper('destroy');
                        $(this).attr("data-new", false);
                        options.cropperButtonSelector
                            .prop("disabled", true);
                        options.cropperResultMessageBoxSelector
                            .empty()
                            .end()
                            .active = false;
                    })
                    .on('show.bs.modal', function (e) {
                        that._trigger("modalshowevent", event, true);
                    })
                    .on('hide.bs.modal', function (e) {
                        that._trigger("modalhideevent", event, true);
                    });

                options.cropperButtonDivSelector.on(
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
                                data.option = "true";
                            }
                            else if (editType === "upload") {
                                data.method = "getCroppedCanvas";
                            }
                        }

                        that._trigger('modalinprogessstatus', event, true);

                        var result = $image.cropper(data.method, data.option,
                            data.secondOption);

                        switch (data.method) {
                            case 'scaleX':
                            case 'scaleY':
                                $(this).data('option', -data.option);
                                break;
                            case 'reset':
                                options.cropperStatusBtnSelector.prop("disabled", true);
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

                        var currentData = $image.cropper("getData", "true");

                        if (JSON.stringify(croppStartingData) === JSON.stringify(currentData))
                        {options.cropperStatusBtnSelector.prop("disabled", true);
                        that._trigger('modalinprogessstatus', event, false);}

                    });

            },

            _initEditModal: function(){
                this._initEditModalId();
                this._initEditModalImgId();
                this._initCropperResultMessageBoxSelector();
                this._initCropperButtonDivSelector();
                this._initCropperButtonSelector();
                this._initCropperStatusBtnSelector();
                this._initCropperRotateBtnSelector();
                this._initEditModalEventHandler();
            },

           _initStatusDataName: function () {
                var options = this.options;
                if (options.statusDataName === undefined) {
                    options.statusDataName = "file-pk";
                }
            },

            _initSortableHandleSelector: function () {
                this.options.sortableHandleSelector = this._getSortableHandle();
            },

            _getSortableHandle: function () {
                var options = this.options,
                    sortableHandleSelector;
                if (options.sortableHandleSelector === undefined) {
                    return ".sortableHandle";
                } else if (options.sortableHandleSelector instanceof $) {
                    return sortableHandleSelector.selector;
                }
            },

            _initSortable: function() {
                this._initSortableHandleSelector();
                var options = this.options,
                    sortableOptions = options.sortableOptions,
                    that = this,
                    defaultSortableOptions = {
                        delay: 500,
                        scrollSpeed: 40,
                        handle: options.sortableHandleSelector,
                        helper: "clone",
                        axis: "y",
                        opacity: 0.9,
                        cursor: "move",
                        start: function(e, ui){that._trigger("sortableStart");},
                        stop: function(e, ui){
                            that._trigger("sortableStop");
                        },
                        update: function(e, ui){that._trigger("sortableUpdate");}
                    };
                if (sortableOptions) {
                    delete sortableOptions.handle;
                    sortableOptions = $.extend(defaultSortableOptions, sortableOptions);
                }
                else{
                    sortableOptions = defaultSortableOptions;
                }

                this.options.filesContainer.sortable(
                    sortableOptions
                ).disableSelection();
            },

            _initSpecialOptions: function () {
                this._super();
                this._initStatusDataName();
                this._initSortable();
                this._initEditModal();
            }

        }
    );
})(jQuery, window, document);