$(document).ready(function () {

    var myElement = $("#country");
    var ipAddress = $("#ip");
    // myElement.html("<p>Hello World</p>");
    $.get("http://ip-api.com/json", function (response) {
        myElement.html(response.country + ", " + response.region);
        ipAddress.html(response.query);
    }, "jsonp");
    // $.get("https://ipinfo.io", function (response) {
    //     console.log(response.city, response.country);
    // }, "jsonp");
});