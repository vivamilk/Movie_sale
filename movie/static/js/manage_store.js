$(document).ready(function () {
    $("body").delegate(".senior-admin-p-add", "click", function (event) {
        var add = $(this).parent().parent();
        var store_id = add.find(".storeid").val();
        var email = add.find(".email").val();
        var region= add.find(".region").val();
         var item_info = `<tr>
                    <td>${store_id}</td>
                    <td><h5>${email}</h5></td>
                    <td><h5>${region}</h5></td>
                </tr>`
        $.ajax({
            url:'/manage/add_store',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({'store_id': store_id, 'email':email, 'region':region}),
            success: function(data){
                alert("Add item successfully!");
            },
            error: function(data){
                alert(data.responseJSON.message);
            }
        })
        var total_table = add.parent().parent();
        $(total_table).append(item_info);
    });
});