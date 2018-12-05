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
                count_item()
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    count_item();
    function count_item(){
        $.ajax({
            url: '/shopping/count_item',
            success: function(data){
                console.log(data);
                $('.badge').html(data);
            }
        });
    }
});
// span class = badge  press the button will increase the number of badge
//