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

function StandardPost(args) {
    if ("error" in args) {
        alert(args["error"]);
    }
    else {
        var form = $("<form target='paypal' method='post'></form>"), input;
        form.attr({ "action": "https://www.sandbox.paypal.com/cgi-bin/webscr" });
        for (arg in args) {
            input = $("<input type='hidden'>");
            input.attr({ "name": arg });
            input.val(args[arg]);
            form.append(input);
        }
        form.appendTo(document.body);
        form.submit();
        document.body.removeChild(form[0]);
    }
}

function send_checkout() {
    $('#co').click(function () {
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

function bind_update_function() {
    $('#cart_product .admin-p-add-item').unbind();
    $('#cart_product .admin-p-remove-item').unbind();
    $('#cart_product .admin-p-add-item').click(function () {
        var item_id = this.id;
        $.ajax({
            url: '/shopping/' + item_id,
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({ 'number': 1 }),
            success: function (response) {
                count_item();
                get_cart_item();
                $('.dropdown-toggle').dropdown('toggle');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
    $('#cart_product .admin-p-remove-item').click(function (e) {
        e.preventDefault();
        var item_id = this.id;
        $.ajax({
            url: '/shopping/remove/' + item_id,
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({ 'number': 1 }),
            success: function (response) {
                count_item();
                get_cart_item();
                $('.dropdown-toggle').dropdown('toggle');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
}

function get_cart_item() {

    $.ajax({
        url: '/shopping/get_items',
        type: "POST",
        success: function (data) {
            console.log(data);
            $('#cart_product').empty();
            let total = 0;
            for (var keys in data) {
                var product_id = data[keys]['movieID'];
                var title = data[keys]['title'];
                var price = data[keys]['price'];
                var amount = data[keys]['amount'];
                var subtotal = parseFloat(price) * parseFloat(amount);
                subtotal = subtotal.toFixed(2);
                total += parseFloat(subtotal);
                let item =    `             
                <li>
                <span class="item">
                    <span class="item-left">
                        <span class="item-info">
                            <span><b>${title}</b></span>
                            <span>$${price}</span>
                        </span>
                    </span>
                    <span class="item-right">
                    <a href="#" id=${product_id} class="del-btn admin-p-remove-item pull-right"><span class="fas fa-minus"> </span></a>
                    ${amount}
                    <a href="#" id=${product_id} class="del-btn admin-p-add-item"><span class="fas fa-plus"> </span></a>
                    </span>
                </span>
                </li>
                `;

                $('#cart_product').append(item);
            }
            total = total.toFixed(2);
            var button_item = `
            <div class="dropdown-divider"></div>
            <li><p class="text-center">Total Price: ${total}</p></li>
            <li id="co" style="text-align:center;"><a class="btn btn-warning"><b>Check Out</b></a></li>
            `;
            $('#cart_product').append(button_item);
            bind_update_function();
            send_checkout();
        }
    })
}

$(document).ready(function () {
    $('.movie-list').delegate('button', "click", function (event) {
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
    count_item();
    get_cart_item();
});