async function fetchYear() {
    // return (await fetch("/getYear")).json()
    return [1,2,3]
}

async function popupYear() {

    const data = await fetchYear(1)
    // jquery create element/dom
    // jquery selector
    $("#shoppingcart-content").html(
        data.map(x=>$(`<p>${x}</p>`))
    )
}

function change_store_id() {
    var id = document.getElementById("store_id_select").value;
    $.ajax({
        url: '/store_id_listener',
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'store_id': id}),
        success: function (response) {
            console.log(response);
            var bar = document.getElementById("search_bar");
            bar.submit();
        },
        error: function (error) {
            console.log(error);
        }
    });
}