function get_all_button() {
    return $(".movie-list").find("button")
}

$(document).ready(function () {
    let but = get_all_button();
    $('.movie-list').delegate('button', "click", function(event){
        var movie_id = this.id;
         $.ajax({
            url: '/shopping/' + movie_id,
            contentType: "application/json; charset=utf-8",
            type:"POST",
            data: JSON.stringify({'number':1}),
            success: function(response) {
            console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    //
    // $("button#3").click(function () {
    //     $.ajax({
    //         url: '/shopping/3',
    //         contentType: "application/json; charset=utf-8",
    //         type:"POST",
    //         data: JSON.stringify({'number':1}),
    //         success: function(response) {
    //         console.log(response);
    //         },
    //         error: function(error) {
    //             console.log(error);
    //         }
    //     });
    // });
})
// span class = badge  press the button will increase the number of badge
//