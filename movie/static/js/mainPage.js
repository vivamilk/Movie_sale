$(document).ready(function () {

    var myElement = $("#country");
    // myElement.html("<p>Hello World</p>");
    $.get("http://ip-api.com/json", function (response) {
        myElement.html(response.country + ", " + response.region);
    }, "jsonp");
    // $.get("https://ipinfo.io", function (response) {
    //     console.log(response.city, response.country);
    // }, "jsonp");
});