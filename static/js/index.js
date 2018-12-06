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