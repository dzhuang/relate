////document.write(5 + 6);
//
//var gentime = document.getElementById('gen_time').innerHTML;
//
////document.getElementById('gen_time').innerHTML = "abcd";
//
////document.write(gentime+"</br>");
//
//var regex = /\d{4}\/\d+\/\d+ \d+:\d+:\d+$/g;
//var datetime = regex.exec(gentime);
//
////document.write(datetime);
//
////alert(datetime);
//
//function toJSDate(dateTime) {
//    var dateTime = dateTime.toString().split(" ");
//    var date = dateTime[0].split("/");
//    var time = dateTime[1].split(":");
//    //alert(date[1]);    
//    //(year, month, day, hours, minutes, seconds, milliseconds)
//    return new Date(date[0], date[1]-1, date[2], time[0], time[1], time[2], 0);
//}
//
//var d = toJSDate(datetime);
//
//
//var date_string = d.toLocaleDateString();
//
//var time_string = d.toLocaleTimeString();
//
////alert(date_string);
//
////alert(time_string);
//
//var now = new Date();
//
////alert(d.toLocaleDateString());
//
////alert(now.toLocaleDateString());
//
//
//// compare date time
//alert((d>now)-(d<now));

//var date1 = new Date(2015, 8, 1);
//var date2 = new Date(2015, 8, 1);
//
//alert (date1 == date2)
//
//alert((date1>date2)-(date2>date1))


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



var timeArray = ["2015/5/18 0:00:00", "2015/6/18 0:00:00", "2015/7/18 0:00:00", "2015/8/18 0:00:00"];

var cssArray = ["basic.css", "basic_1.css", "basic_2.css", "basic_3.css"];

//var thedate = timeArray[0];
//var cssFile = cssArray[0];
var temp_id = timeArray.length -1;
function get_css_name(){
    var html_date = get_HTML_date();
    //alert(html_date);
    // 时间小于第1个，则用第1个css
    if ((toJSDate(timeArray[0])>html_date) - (toJSDate(timeArray[0])<html_date) > 0){
        return cssArray[0]
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

    return cssArray[temp_id]
    
}


function changeCSS(cssFile, cssLinkIndex) {
    var oldlink = document.getElementsByTagName("link").item(cssLinkIndex);
    var newlink = document.createElement("link");
    newlink.setAttribute("rel", "stylesheet");
    newlink.setAttribute("type", "text/css");
    var css_path = "http://127.0.0.1:8000/static/css/"
    
    newlink.setAttribute("href", css_path+cssFile);
    document.getElementsByTagName("head").item(0).replaceChild(newlink, oldlink);
}


document.onload=changeCSS(get_css_name(), 0);