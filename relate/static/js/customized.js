// {{{ pdfjs loader


// Decide indentation of ul or ol on mobile phone
// references: http://stackoverflow.com/a/7640666/3437454

$(function () {
    if (matchMedia('only screen and (max-width: 767px)').matches) {
        $('.container').has('form').children('ul,ol').each(function () {
            $(this).smallscreen_pdf_indent();
        });
    }
    
    // for non_mobile tags, make it invisible for max-width: 767px
    // http://www.w3schools.com/bootstrap/bootstrap_ref_css_helpers.asp
    $('non_mobile').addClass("hidden-xs");
});

// If a li contains id with pdfviewer_div, then all its sibling will have no 
// indentation.
$.fn.smallscreen_pdf_indent = function () {
    var $this = $(this);
    if ($this.find("[id$='pdfviewer_div']").length > 0) {
        $this.css('padding-left', 0);
        $this.children('ul,ol,li').each(function () {
            console.log(this);
            $(this).smallscreen_pdf_indent();
        });
    }
}



$(document).ready(generate_download_pdf_view());

function generate_download_pdf_view() {
    var all_li = $(".file_download_view");
    for (var i = 0; i < all_li.length; i++) {
        var element_i = all_li[i]
        var url_i = $(element_i).attr("href");
        var file_id = get_file_name(url_i);
        //        if ($(this).parent().is("li")) {
        //            $(this).parent().parent().addClass("pdf_list_block")
        //        }
        //console.log(file_id);
        if ($(file_id).length == 0) {
            $('<a href="#" onclick="embed_viewer(this)" id="' + file_id + '"><i class="fa fa-eye" title="在线查看"></i></a> <div id="' + file_id + '_pdfviewer_div"></div>').insertAfter($(element_i));
            $(element_i)
                .attr("id", file_id + "_download_link")
                .after(" &middot; ");
        }
    }
}


// http://stackoverflow.com/a/2502890/3437454

$.fn.splitUp = function (splitBy, wrapper) {
    $all = $(this).find('>*');
    var fragment = Math.ceil($all.length / splitBy);
    for (i = 0; i < fragment; i++)
        $all.slice(splitBy * i, splitBy * (i + 1)).wrapAll(wrapper);
    return $(this);
}

//usage:
//
//$('ul#slides').splitUp(4,'&lt;li class=splitUp&gt;&lt;ul&gt;')
//or:
//
//$('div#slides').splitUp(3,'&lt;div/&gt;')


function get_file_name(url) {
    var filename = url.substring(url.lastIndexOf('/') + 1).replace(/\.[^/.]+$/, "");
    return filename;
}

function embed_viewer(item) {
    // alert on browser which is below IE 9
    var div = document.createElement("div");
    div.innerHTML = "<!--[if lt IE 9]><i></i><![endif]-->";
    var isIeLessThan9 = (div.getElementsByTagName("i").length == 1);
    if (isIeLessThan9) {
        alert("ie10以下的版本的浏览器不支持预览");
    } else {

        var hrefID = item.id + "_download_link";
        var viewpath = $("#" + hrefID).attr("href");
        //var filename = viewpath.substring(viewpath.lastIndexOf('/')+1);
        var display_DIV_ID = item.id + "_pdfviewer_div";

        if (matchMedia('only screen and (max-width: 767px)').matches) {
            $("#" + display_DIV_ID).html(
                "<iframe src = '/static/pdf.js/web/viewer.html?file=" + viewpath + "' width='100%' height='450' allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>"
            );
        }
        else {
            
            if (viewpath.indexOf("non-slide") > 0){$("#" + display_DIV_ID).html(
                "<iframe src = '/static/pdf.js/web/viewer.html?file=" + viewpath + "' width='630' height='860' allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>"
            );}
            else {$("#" + display_DIV_ID).html(
                "<iframe src = '/static/pdf.js/web/viewer.html?file=" + viewpath + "' width='800' height='450' allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>"
            );}
            
            
        }

        //$("#" + display_DIV_ID).parent('li').parent('ul').css('padding-left',0)
        $('html, body').animate({
            scrollTop: $(item).offset().top
        }, 1000);
        $(item).attr("onclick", "close_viewer(this);").attr("title", "关闭在线查看").html("<i class='fa fa-eye-slash'></i>");
    }
}

function close_viewer(item) {
    var display_DIV_ID = item.id + "_pdfviewer_div";
    $("#" + display_DIV_ID).html("");
    //$("#" + display_DIV_ID).slideUp("slow", function(){ $("#" + display_DIV_ID).html("");});
    //$("#" + display_DIV_ID).attr("style", "")
    $(item).attr("onclick", "embed_viewer(this)").attr("title", "在线查看").html("<i class='fa fa-eye'></i>");
    $('html, body').animate({
        scrollTop: $(item).offset().top
    }, 1000);
}

// }}}

/**
 * detect IE
 * returns version of IE or false, if browser is not Internet Explorer
 */
function detectIE() {
    var ua = window.navigator.userAgent;

    var msie = ua.indexOf('MSIE ');
    if (msie > 0) {
        // IE 10 or older => return version number
        return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
    }

    var trident = ua.indexOf('Trident/');
    if (trident > 0) {
        // IE 11 => return version number
        var rv = ua.indexOf('rv:');
        return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
    }

    var edge = ua.indexOf('Edge/');
    if (edge > 0) {
       // IE 12 => return version number
       return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
    }

    // other browser
    return false;
}


//$(function () {
//    if (detectIE() == true){
//        
//        $('foot').hide();
//    
//    }
//    
//});

function getAnchor(url)
{
    var index = url.lastIndexOf('#');
    if (index != -1)
        return url.substring(index);
}


$(function () {
    // {{{ enable accordion deprecated
    $(".accordion").accordion({
        active: false,
        collapsible: true,
    });
    // }}}
    
    // {{{ enable file download filetype icon
    $("[id^='for_download_file_']").each(function () {
        var file_name = $(this).attr('id');
        var ext = file_name.split('.').pop().toLowerCase();
        var fa_file_icon_class = "";
        if (['xls', 'xlst', 'xlsm'].indexOf(ext) >= 0) {
           fa_file_icon_class ="file-excel-o";
        }
        else if(['doc','docx','dot','dotm','docm'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-word-o";
        }
        else if(['jpg','png','jpeg','gif','bmp'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-image-o";
        }
        else if(['ppt','pptx','pot','potx','pps','ppsx'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-powerpoint-o";
        }
        else if(['pdf'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-pdf-o";
        }
        else if(['zip', 'rar'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-zip-o";
        }
        else if(['text'].indexOf(ext) >= 0) {
            fa_file_icon_class ="file-text-o";
        }
        else{
            fa_file_icon_class ="file-o";
        };
        
        $(this).addClass("fa fa-" + fa_file_icon_class);
        
    });
    // }}}

    // {{{ open accordion on getanchor
    
//    var anchor = getAnchor(location.href);
//    $(anchor).next().children('.collapse').show();
    
    // }}}

});

// deprecated
$(".ui-state-disabled").unbind("click");

function locationHashChanged() {
    var anchor = getAnchor(location.href);
    var collapse_block = $(anchor).next().children('.collapse');
    collapse_block.collapse('show');
    
};


window.onhashchange = locationHashChanged;
