function get_all_button() {
    return $(".movie-list").find("button")
}

function StandardPost(args)
    {   if ( "error" in args)
        {
            alert(args["error"]);
        }
        else
        {
            var form = $("<form target='paypal' method='post'></form>"), input;
            form.attr({"action":"https://www.sandbox.paypal.com/cgi-bin/webscr"});
            for (arg in args)
            {
                input = $("<input type='hidden'>");
                input.attr({"name":arg});
                input.val(args[arg]);
                form.append(input);
            }
            form.appendTo(document.body);
            form.submit();
            document.body.removeChild(form[0]);
        }
    }

$(document).ready(function () {
    let but = get_all_button();
    $('.movie-list').delegate('button', "click", function (event) {
        var movie_id = this.id;
        $.ajax({
            url: '/shopping/' + movie_id,
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({'number': 1}),
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
    count_item();

    function count_item() {
        $.ajax({
            url: '/shopping/count_items',
            type: 'POST',
            success: function (data) {
                console.log(data);
                $('.badge').html(data);
            }
        });
    }
    get_cart_item()
    function get_cart_item() {
        $.ajax({
            url: '/shopping/get_items',
            type: "POST",
            success: function (data) {
                $('#cart_product').empty();
                let total = 0;
                for (var keys in data) {
                    var product_id = data[keys]['movieID'];
                    var title = data[keys]['title'];
                    var price = data[keys]['price'];
                    var amount = data[keys]['amount'];
                    var subtotal = parseFloat(price) * parseFloat(amount);
                    subtotal = subtotal.toFixed(2);
                    total += parseFloat(subtotal)
                    let item = `
                        <div class="row top-buffer">
                            <div class="col-md-2" id=${product_id}><img class="img-responsive" src="/static/posters/${product_id}.jpg/"/></div>
                            <div class="col-md-2 text-center"><h5>${title}</h5></div>
                            <!--<div class="col-md-2 text-center amount"><h5></h5></div>-->
                            <div class="col-md-2 text-center price"><h5>\$${price} (X${amount})</h5></div>
                            <!--<div class="col-md-3 text-center"><h5>${subtotal}</h5></div>-->
                       </div>
                    `;
                    $('#cart_product').append(item);
                }
                    total = total.toFixed(2);
                    var button_item =  `<div class="row top-buffer text-right"><hr>
                                    <div class="col-md-3"><h5>Total Price: ${total}</h5></div>
                                    <div class="col-md-3"><button id="co" type="button" style="float:right;" class="btn btn-default">
                                    Checkout</button></div>`
                    $('#cart_product').append(button_item);
                    send_checkout();
            }
        })
    }
    function send_checkout(){
        $('#co').click(function(){
            $.ajax({
                url: '/checkout',
                type: 'POST',
                success: function (response) {
                    console.log(response);
                    StandardPost(response);
                },
                error: function (error) {
                    console.log(error);
                }
            });
        })
    }
});