$(document).ready(function () {
    $('.movie-detail').delegate('button', "click", function (event) {
        var movie_id = this.id;
        $.ajax({
            url: '/shopping/' + movie_id,
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({ 'number': 1 }),
            success: function (response) {
                console.log(response);
                count_item();
                get_cart_item();
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});