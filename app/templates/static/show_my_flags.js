$.ajax({

                  url: '/api/get_user',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    if(! isEmptyObject(jdata.Error)){
                      $(location).attr('href', '/')
                    } 
                    else{
                      $("#auth").html('<span class="auth-text" id="username"></span><p><span class="money" id="coins">$</span></p><p><a href="add_page" class="lk-links add">Add merchandise</a></p><p><a href="orders" class="lk-links">My orders</a></p>  <p><a href="send_page" class="lk-links">Send money</a></p><p class="logout"><a href="" onClick="logout()">Logout</a></p>');

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

                  url: '/api/get_my_flags',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    var jsonData=jdata.my_flags
                    $(jsonData).each(function (index, item) {
                    $('#flags_table tbody').append(
                        '<tr id="'+ item.name  +'"><td>' + item.name+
                        '</td><td>' + item.cost +
                        '</td><td>' + item.in_stock +
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

function add_flag(){
{
        
        var name = document.getElementById("input-name").value;
        var description = document.getElementById("input-description").value;
        var in_stock = document.getElementById("input-in_stock").value;
        var cost = document.getElementById("input-cost").value;


        

          $.ajax({
    url: '/api/add',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { "name": name, "description": description, "in_stock": in_stock, "cost": cost} ),
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
        $('#flags_table tbody').append(
                        '<tr id="'+ name  +'"><td>' + name+
                        '</td><td>' + cost +
                        '</td><td>' + in_stock +
                        '</td></tr>'
                    );
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