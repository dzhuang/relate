function toJSDate(dateTime) {
    var dateTime = dateTime.toString().split(" ");
    var date = dateTime[0].split("/");
    var time = dateTime[1].split(":");
    //alert(date[1]);    
    //(year, month, day, hours, minutes, seconds, milliseconds)
    return new Date(date[0], date[1]-1, date[2], time[0], time[1], time[2], 0);
}

function get_HTML_date(){
    var gentime = document.getElementById('gen_time').innerHTML;
    var regex = /\d{4}\/\d+\/\d+ \d+:\d+:\d+$/g;
    var datetime = regex.exec(gentime);
    var d = toJSDate(datetime);
    return d;    
}



var timeArray = ["2015/9/24 14:30:00", "2015/10/08 14:30:00", "2015/10/15 14:30:00", "2015/10/22 14:30:00"];

var fileArray = ["basic.css", "basic_1.css", "basic_2.css", "basic_3.css"];

//var fileArray = ["basic.js", "basic_1.js", "basic_2.js", "basic_3.js"];

//var thedate = timeArray[0];
//var cssFile = cssArray[0];
var temp_id = timeArray.length -1;
function get_file_name(){
    var html_date = get_HTML_date();
    //alert(html_date);
    // 时间小于第1个，则用第1个css
    if ((toJSDate(timeArray[0])>html_date) - (toJSDate(timeArray[0])<html_date) > 0){
        return fileArray[0]
    }
    else
        for (var i=0; i<timeArray.length; i++){
            date_i = timeArray[i];
            if ((toJSDate(date_i)>html_date) - (toJSDate(date_i)<html_date) < 0){
                //alert(i);
                temp_id=i;
                if(i<timeArray.length-1){
                    date_j = timeArray[i+1];
                    if ((toJSDate(date_j)>html_date) - (toJSDate(date_j)<html_date) >= 0 ){
                        temp_id = i+1;
                        }   
                }

            }

        }

    return fileArray[temp_id]
    
}


//function changeCSS(cssFile, cssLinkIndex) {
//    var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);
//    var newlink = document.createElement("link");
//    newlink.setAttribute("rel", "stylesheet");
//    newlink.setAttribute("type", "text/css");
//    var css_path = "http://127.0.0.1:8000/static/css/"
//    
//    newlink.setAttribute("href", css_path+cssFile);
//    document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
//}
//document.onload=changeCSS(get_file_name(), 0);


function changeJS(JSFile) {
    var JS_path = "http://www.learningwhat.com/static/JS/"
    $("#loadedJS").attr("src", JS_path+JSFile);
}

function changeCSS(CSSFile) {
    var CSS_path = "http://www.learningwhat.com/static/css/"
    $("#basicCSS").attr("href", CSS_path+CSSFile);
}

document.onload=changeCSS(get_file_name());
//document.onload=changeJS(get_file_name());