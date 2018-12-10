$(document).ready(function () {

    $("body").delegate(".admin-p-remove","click",function(event) {
        var remove = $(this).parent().parent();
        var remove_id = remove.find(".admin-p-remove").attr("remove_id");
        var store_id = $( "#store_id_select option:selected" )[0].value;
        remove.hide();
        $.ajax({
            url: '/manage/delete_movie',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({'movie_id': remove_id, 'store_id':store_id}),
            success: function(data){
                alert("Delete Successfully");
            }
            })
    });

    $('body').delegate(".admin-p-update", "click", function (event) {
        var add = $(this).parent().parent();
        var movid_id = add.find(".movieid").val();
        var imdb_id = add.find(".imdbid").val();
        var name = add.find(".name").val();
        var inventory_amount = add.find(".inventory").val();
        var price = add.find(".sale-price").val();
        var cost = add.find(".cost").val();
        var store_id = $( "#store_id_select option:selected" )[0].value;
        $.ajax({
            url:'/manage/update_movie',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({'store_id': store_id, 'price':price, 'cost':cost, 'name':name, 'inventory': inventory_amount}),
            success: function(data){
                alert("Add item successfully!");
            },
        });
    });

    $("body").delegate(".admin-p-add","click",function(event) {
        var add = $(this).parent().parent();
        var movid_id = add.find(".movieid").val();
        var imdb_id = add.find(".imdbid").val();
        var name = add.find(".name").val();
        var inventory_amount = add.find(".inventory").val();
        var price = add.find(".sale-price").val();
        var cost = add.find(".cost").val();
        var item_info = `<tr>
                    <!--<td>${movid_id}</td>-->
                    <td><input type="text" class="form-control movieid" value=${movid_id} readonly></td>
                    <td><input type="text" class="form-control imdbid" value=${imdb_id}></td>
                        <div class="img-container">
                            <img class="picture" height="42" width="42" alt="select a picture" title="select a picture"
                                 src="static/posters/0.jpg"/>
                            <div class="img-centered">
                                <label class="img-label" for="my-file-selector'.$product_id.'">
                                    <input fn="'.$image.'" class="image" id="my-file-selector'.$product_id.'"
                                           type="file" style="display:none;" accept="image/x-png,image/gif,image/jpeg">
                                </label>
                            </div>
                        </div>
                    </td>
                    <td><input type="text" class="form-control name" value=${name}></td>
                    <td><input type="text" class="form-control inventory" value=${inventory_amount}></td>
                    <td><input type="text" class="form-control price" value=${price}></td>
                    <td><input type="text" class="form-control cost" value=${cost}></td>
                    <td>
                        <a href="#" remove_id=${movid_id} class="del-btn admin-p-remove"><span
                            class="fas fa-trash-alt"></span></a>
                        <a href="#" update_id=${movid_id} class="del-btn admin-p-update"><span
                            class="fas fa-redo-alt"></span></a>
                    </td>
                </tr>`;
        var total_table = add.parent().parent();
        $(total_table).append(item_info);
        var store_id = $( "#store_id_select option:selected" )[0].value;
        $.ajax({
            url:'/manage/add_movie',
            contentType: "application/json; charset=utf-8",
            type: "POST",
            data: JSON.stringify({'movie_id': movid_id, 'imdb_id': imdb_id,'store_id': store_id, 'price':price, 'cost':cost, 'name':name, 'inventory': inventory_amount}),
            success: function(data){
                alert("Add item successfully!");
            },
            error: function(data){
                alert(data.responseJSON.message);
            }
        })
    })
});