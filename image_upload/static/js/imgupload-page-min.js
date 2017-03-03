function assignOrder(){"use strict";var t=0;$("#fileupload > table > tbody > tr").each(function(){$(this).data("order").new_ord=t,t+=1}),$(".btn-srt").each(function(){$(this).removeClass("hidden")}),$("tr:nth-child(1) > td.td-srt > .up").addClass("hidden"),$("tr:nth-child(1) > td.td-srt > .top").addClass("hidden"),$("tr:nth-child(2) > td.td-srt > .top").addClass("hidden"),$("tr:nth-last-child(1) > td.td-srt > .down").addClass("hidden")}$(document).ready(function(){"use strict";$(".relate-save-button").each(function(){$(this).attr("formaction",window.location.pathname)}),$("#past-submission_dropdown").addClass("hidden"),new Clipboard(".btn-data-copy")}),$(".btn-srt-tbl").on("click",function(){"use strict";function t(){return $(".relate-save-button").addClass("disabled"),$("#srt_prgrs").html('<img src="/static/images/busy.gif" %}" alt="Busy indicator">').show(),r=[],$("#fileupload > table > tbody > tr").each(function(){$(this).data("order").new_ord!==$(this).data("order").old_ord&&r.push($(this).data("order"))}),r.length>0?(o=$.ajax({method:"POST",url:$("#ord-form").attr("action"),data:$("#ord-form").serialize()+"&chg_data="+JSON.stringify(r)}).done(function(t){console.log("ok"),$("#fileupload > table > tbody > tr").each(function(){$(this).data("order").new_ord=$(this).data("order").old_ord,$("[class*=btn-srt]").removeClass("disabled"),$(".relate-save-button").removeClass("disabled")}),$("#srt_prgrs").html(t.message),window.setTimeout(function(){$("#srt_prgrs").fadeOut()},3e3)}).fail(function(t){console.log(t),$("#srt_prgrs").html(gettext("Failed!")+" "+t.responseJSON.message),window.setTimeout(function(){$("#srt_prgrs").fadeOut()},3e3)}),!1):void $("#fileupload > table > tbody > tr").each(function(){console.log("unchanged??"),$(this).data("order").new_ord=$(this).data("order").old_ord,$("[class*=btn-srt]").removeClass("disabled"),$(".relate-save-button").removeClass("disabled")})}var e,a,d,s,i,n,r,o;$(this).addClass("hidden"),$("#fileupload > .fileupload-buttonbar > div > *").not(".btn-srt-tbl-cfm").not(".btn-srt-tbl").addClass("disabled"),$(".btn-srt-tbl-cfm").removeClass("hidden"),$(".td-dl").each(function(){$(this).addClass("hidden")}),$(".td-srt").each(function(){$(this).removeClass("hidden")}),assignOrder(),e=$(".up"),e.click(function(){$("[class*=btn-srt]").addClass("disabled");var a=$(this).parents("tr");0!==a.index()&&(s=a,i=a.prev(),a.prev().before(a),e=$(".up"),assignOrder(),t())}),a=$(".down"),d=a.length,a.click(function(){$("[class*=btn-srt]").addClass("disabled");var e=$(this).parents("tr");e.index()!==d-1&&(e.next().after(e),a=$(".down"),assignOrder(),t())}),n=$(".top"),n.click(function(){$("[class*=btn-srt]").addClass("disabled");var e=$(this).parents("tr");0!==e.index()&&1!==e.index()&&($(".table").prepend(e),e.css("color","#f60"),n=$(".top"),assignOrder(),t())})}),$(".btn-srt-tbl-cfm").on("click",function(){"use strict";$(this).addClass("hidden"),$(".btn-srt-tbl").removeClass("hidden"),$(".td-dl").each(function(){$(this).removeClass("hidden")}),$(".td-srt").each(function(){$(this).addClass("hidden")}),$("#fileupload > .fileupload-buttonbar > div > *").not(".btn-srt-tbl-cfm").not(".btn-srt-tbl").removeClass("disabled")});var clicked_row;$("#fileupload").on("click",".btn-edit-image",function(){"use strict";clicked_row=$(event.target).closest("tr")}),window.addEventListener("DOMContentLoaded",function(){"use strict";$(".modal .modal-body").css("overflow-y","auto").css("max-height",.9*$(window).height()).css("margin",0).css("border",0);var t,e,a,d,s,i,n;$("body").on("shown.bs.modal",function(){function r(t,e){var a=$("#crp-result");t===!0?a.addClass("alert alert-success").html(e):a.addClass("alert alert-danger").html(e),window.setTimeout(function(){a.removeClass().html("")},3e3)}function o(e){var a,d,s,i,n;a=t.getContainerData(),t.setCropBoxData({width:2,height:2,top:a.height/2-1,left:a.width/2-1}),t.rotate(e),d=t.getCanvasData(),s=d.width*(a.height/d.height),s>=a.width?(i=d.height*(a.width/d.width),n={height:i,width:a.width,top:(a.height-i)/2,left:0}):n={height:a.height,width:s,top:0,left:(a.width-s)/2},t.setCanvasData(n).setCropBoxData(n),$(".btn-crp-submit").removeClass("disabled"),$(".btn-crp-reset").removeClass("disabled")}function l(t){return"number"!=typeof t?"":t>=1e9?(t/1e9).toFixed(2)+" GB":t>=1e6?(t/1e6).toFixed(2)+" MB":(t/1e3).toFixed(2)+" KB"}e=document.querySelector("#image"),a=document.getElementById("dataX"),d=document.getElementById("dataY"),s=document.getElementById("dataHeight"),i=document.getElementById("dataWidth"),n=document.getElementById("dataRotate"),$(".img-container img").css("max-height",.8*$(window).height()),t=new Cropper(e,{checkOrientation:!1,autoCrop:!0,autoCropArea:1,strict:!0,movable:!1,zoomable:!1,minContainerheight:.8*$(window).height(),cropstart:function(t){$(".btn-crp-submit").removeClass("disabled"),$(".btn-crp-reset").removeClass("disabled")},crop:function(t){a.value=Math.round(t.x),d.value=Math.round(t.y),s.value=Math.round(t.height),i.value=Math.round(t.width),n.value=Math.round(t.rotate)}}),$(".btn-crp-rtt").click(function(){o($(this).data("step"))}),$(".btn-crp-preview").click(function(){var e=$(".cropper-container").hasClass("hidden"),a=t.getCroppedCanvas();e?($(".cropper-container").removeClass("hidden"),$("#preview").addClass("hidden").html(""),$(this).html("<i class='fa fa-eye'></i> <span>"+gettext("Preview")+"</span>"),$(".btn-crp-rtt").removeClass("hidden"),$(".btn-crp-reset").removeClass("hidden")):($(".cropper-container").addClass("hidden"),$("#preview").removeClass("hidden").html(a),$(this).html("<i class='fa fa-pencil'></i> <span>"+gettext("Edit")+"</span>"),$(".btn-crp-rtt").addClass("hidden"),$(".btn-crp-reset").addClass("hidden"))}),$(".btn-crp-submit").click(function(){var e,a,d,s,i,n,o;return $(this).addClass("disabled"),$(".modal-footer > button").addClass("disabled"),e=$("#dataX").val(),a=$("#dataY").val(),d=$("#dataWidth").val(),s=$("#dataHeight").val(),i=$("#dataRotate").val(),""===e||""===a||""===d||""===s||""===i?($(this).removeClass("disabled"),!1):(n=$.ajax({method:"POST",url:$("#crp-form").attr("action"),data:$("#crp-form").serialize()}).done(function(e){var a=e.file;-1===window.location.pathname.indexOf("/grading/")?$("#thumbnail"+a.pk).prop("src",a.thumbnailUrl):($("#thumbnail"+a.pk).prop("src",a.url),$("#thumbnail"+a.pk).prop("style","width:40vw")),$("#previewid"+a.pk).prop("href",a.url),$("#filename"+a.pk).prop("href",a.url),$("#filetime"+a.pk).prop("title",a.timestr_title).html(a.timestr_short),$("#filesize"+a.pk).html(l(a.size)),t.replace(a.url),r(!0,gettext("Done!")),setTimeout(function(){$("#editPopup").modal("hide")},2e3)}).fail(function(t){o=gettext("Failed!")+" "+t.responseJSON.message,r(!1,o),setTimeout(function(){$("#editPopup").modal("hide")},2e3)}),!1)}),$(".btn-crp-reset").click(function(){t.reset(),$(".btn-crp-submit").addClass("disabled"),$(".btn-crp-reset").addClass("disabled")})}),$("body").on("hidden.bs.modal",".modal",function(){$(".img-container").html(""),$(this).removeData("bs.modal"),t.destroy()})});