
$(document).ready(function () {
    $("body").delegate(".admin-p-remove","click",function(event) {
        var remove = $(this).parent().parent();
        var remove_id = remove.find(".admin-p-remove").attr("remove_id");
        remove.hide();
    });
    $('body').delegate(".admin-p-update", "click", function (event) {
        alert("Update Successfully!");
    });
    $("body").delegate(".admin-p-add","click",function(event) {
        var add = $(this).parent().parent();
        var product_kind_id = add.find(".movieid").val();
        var name = add.find(".name").val();
        var inventory_amount = add.find(".inventory").val();
        var price = add.find(".sale-price").val();
        var cost = add.find(".cost").val();
        var item_info = `<tr>
                    <td>${product_kind_id}</td>
                    <td>
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
                        <a href="#" remove_id=${product_kind_id} class="del-btn admin-p-remove"><span
                            class="glyphicon glyphicon-trash"></span></a>
                        <a href="#" update_id=${product_kind_id} class="del-btn admin-p-update"><span
                            class="glyphicon glyphicon-refresh"></span></a>
                    </td>
                </tr>`
        var total_table = add.parent().parent();
        $(total_table).append(item_info);
    })
    //         data    :    {adminRemoveOrderDetail:1,rid:remove_id},
    //         success    :    function(data){
    //            $("#admin_msg").html(data);
    //            admin_order();
    //         }
    //     })
    // })
});