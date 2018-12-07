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
    var e = document.getElementById("ddlViewBy").value;
    $.ajax({
        url: '/store_id_listener',
        type: 'POST',
        success: function (data) {
            console.log(data);
            $('.badge').html(data);
        }
    });
}