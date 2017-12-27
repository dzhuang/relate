var inputChanged = false;

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

var hasInProgress = false,
    modalIsInProgress = false,
    $fileupload = $("#fileupload"),
    // determine whether submit button is disabled during operation
    isInOperation = false;


function disable_submit_button(bool) {
    $(".relate-save-button").prop("disabled", bool);
}

function getStatusChanged(initialStatus, CurrentStatus) {
    if (!initialStatus) return false;
    return JSON.stringify(initialStatus) !== JSON.stringify(CurrentStatus);
}

$fileupload
    .on("fileuploaddestroyed fileuploadcompleted fileuploadsortablestop", function (e, data) {
        var that = $(this).data('blueimp-fileupload') || $(this).data('fileupload'),
            options = that.options,
            currentStatus = options.getStatus(),
            initialStatus = $(this).data.initialStatus;
        inputChanged = getStatusChanged(initialStatus, currentStatus);
        // disable_submit_button(hasInProgress || isInOperation || modalIsInProgress);
    })
    .on("fileuploadadded", function (e, data) {
        hasInProgress = true;
        disable_submit_button(hasInProgress || isInOperation || modalIsInProgress);
    })
    .on("fileuploadcompleted fileuploadfailed fileuploaddestroyed", function (e, data) {
        var that = $(this).data('blueimp-fileupload') || $(this).data('fileupload'),
            options = that.options;
        hasInProgress = options.filesContainer.children()
                .find('.processing').length > 0;
        disable_submit_button(hasInProgress || isInOperation || modalIsInProgress);
    })
    .on("fileuploadmodalinprogessstatus", function (e, data) {
        modalIsInProgress = data === true;
    })
    .on("fileuploadadd fileuploaddestroy fileuploadsortablestart fileuploadmodalshownevent", function () {
        isInOperation = true;
        disable_submit_button(hasInProgress || isInOperation || modalIsInProgress);
    })
    .on("fileuploadadded fileuploaddestroyed fileuploadfailed fileuploadcompleted fileuploadsortablestop fileuploadmodalhiddenevent", function () {
        isInOperation = false;
        disable_submit_button(hasInProgress || isInOperation || modalIsInProgress);
    })
    .on("fileuploadmodalshowevent", function () {
        // Enable back button to close modal and blueimp gallery
        // http://stackoverflow.com/a/40364619/3437454
        if (getWidthQueryMatch_md_sm_xs())
            window.history.pushState('forward', null, '#edit');
    })
    .on("fileuploadmodalhideevent", function () {
        if (location.hash === '#edit' && getWidthQueryMatch_md_sm_xs())
            window.history.back();
    });


function activate_change_listening() {
    inputChanged = false;

    $(window).on('beforeunload',
        function () {
            if (inputChanged || hasInProgress || modalIsInProgress)
                return gettext('You have unsaved changes on this page.');
        });

    function before_submit(evt) {
        inputChanged = false;

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
    // 'use strict';

    function getAllPks(that) {
        var allPks = [];
        $(that).fileupload("option", "filesContainer")
            .children(".template-download").not('.processing')
            .each(function () {
                allPks.push($(this).data($(that).fileupload("option", "statusDataName")));
            });
        return allPks;
    }

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
            .prop("value", getAllPks($('#fileupload')));
    });

    // activate_change_listening();
});
