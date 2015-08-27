// {{{ pdfjs loader


// decide indentation of ul or ol 
// references: http://stackoverflow.com/a/7640666/3437454

$(function () {
    
    
    if (matchMedia('only screen and (max-width: 767px)').matches){

    $("[id$=_pdfviewer_div]").each(function(){

        $(this).parent('li').parent('ul').css('padding-left',0)
        $(this).parent('li').parent('ul').parent('li').parent('ul').css('padding-left',0)
        
        $(this).parent('li').parent('ol').css('padding-left',0)
        $(this).parent('li').parent('ol').parent('li').parent('ol').css('padding-left',0)
    });
    }
});


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
            $('<a href="#" onclick="embed_viewer(this)" id="' + file_id + '">在线查看</a> <div id="' + file_id + '_pdfviewer_div"></div>').insertAfter($(element_i));
            $(element_i)
                .attr("id", file_id + "_download_link")
                .after(" &middot; ");
        }
    }
}


// http://stackoverflow.com/a/2502890/3437454

$.fn.splitUp=function(splitBy,wrapper) {
    $all= $(this).find('>*');
    var fragment=Math.ceil($all.length/splitBy);  
    for(i=0; i< fragment; i++) 
        $all.slice(splitBy*i,splitBy*(i+1)).wrapAll(wrapper);
    return $(this);
}

//usage:
//
//$('ul#slides').splitUp(4,'&lt;li class=splitUp&gt;&lt;ul&gt;')
//or:
//
//$('div#slides').splitUp(3,'&lt;div/&gt;')

function move_view_div(){
    
}

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

        //alert(href);
        $("#" + display_DIV_ID).html(
            "<iframe src = '/static/pdf.js/web/viewer.html?file=" + viewpath + "' width='100%' height='450' allowfullscreen webkitallowfullscreen mozallowfullscreen></iframe>"
        );
        //$("#" + display_DIV_ID).parent('li').parent('ul').css('padding-left',0)
        $('html, body').animate({
            scrollTop: $(item).offset().top
        }, 1000);
        $(item).attr("onclick", "close_viewer(this);").html("关闭在线查看");
    }
}

function close_viewer(item) {
    var display_DIV_ID = item.id + "_pdfviewer_div";
    $("#" + display_DIV_ID).html("");
    //$("#" + display_DIV_ID).slideUp("slow", function(){ $("#" + display_DIV_ID).html("");});
    //$("#" + display_DIV_ID).attr("style", "")
    $(item).attr("onclick", "embed_viewer(this)").html("在线查看");
    $('html, body').animate({
        scrollTop: $(item).offset().top
    }, 1000);
}

// }}}

// {{{ enable 


$(function () {
    $(".accordion").accordion({
        active: false,
        collapsible: true,
    });
});
$(".ui-state-disabled").unbind("click");



//@media only screen and (max-width : 767px) {
//    
//    non_mobile {
//        display: none !important;
//    }
//
//}


// }}}