$.ajax({

                  url: '/api/get_user',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    if(! isEmptyObject(jdata.Error)){
                      $(location).attr('href', '/')
                    } 
                    else{
                      $("#auth").html('<span class="auth-text" id="username"></span><p><span class="money" id="coins">$</span></p><p><a href="add_page" class="lk-links">Add merchandise</a></p><p><a href="orders" class="lk-links flags">My orders</a></p>  <p><a href="send_page" class="lk-links">Send money</a></p><p class="logout"><a href="" onClick="logout()">Logout</a></p>');

                    var username = jdata.User.username;
                    var coins = jdata.User.coins;
                    $("#username").html(username);
                    $("#coins").html(coins);
                    }

                   },

                    error: function(errorThrown){
                       
                       console.log(errorThrown);
                    }

});



$.ajax({

                  url: '/api/get_orders',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    var jsonData=jdata.orders
                    $(jsonData).each(function (index, item) {
                    $('#orders_table tbody').append(
                        '<tr id="'+ item.name  +'"><td>' + item.name+
                        '</td><td>' + item.description +
                        '<td><button class="myButton" onClick="delete_order(' + "'" + item.name  + "'" + ')">x</button></td>'+
                        '</td></tr>'
                    )
                });

                   },

                    error: function(errorThrown){
                       
                       console.log(errorThrown);
                    }

        });  


function isEmptyObject(obj) {
    for (var i in obj) {
        if (obj.hasOwnProperty(i)) {
            return false;
        }
    }
    return true;
}

function delete_order(name){
{
        
        $("#" + name).html("");
        console.log(name)

          $.ajax({
    url: '/api/delete_order',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { "name": name } ),
    processData: false,
    success: function( data, textStatus, jQxhr ){
        myObjStr = JSON.stringify(data);
        json = JSON.parse(myObjStr)
        error = json['Error']
        success = json['Ok']
        if(! isEmptyObject(error)){
        alertify.error(json['Error']);
        }
        if(! isEmptyObject(success)){
        alertify.success(json['Ok']);
        }

    },
    error: function( jqXhr, textStatus, errorThrown ){
        console.log( errorThrown );
    }
});


}

}


function logout(){

$.ajax({

                  url: '/api/logout',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    $(location).attr('href', '/')
                   },

                    error: function(errorThrown){
                       $(location).attr('href', '/lk')
                       console.log(errorThrown);
                    }

});

}