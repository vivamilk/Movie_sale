$(document).ready(function () {
        $("button#3").click(function () {
            $.ajax({
                url: '/shopping/3',
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
});