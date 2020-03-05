$.ajax({

                  url: '/api/get_flags',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    var jsonData=jdata.flags
                    $(jsonData).each(function (index, item) {
                    $('#flags_table tbody').append(
                        '<tr><td>' + item.name+
                        '</td><td>' + item.cost +
                        '</td><td>' + item.in_stock +
                        '<td><button class="myButton" onClick="buy(' + "'" + item.name  + "'" + ')">buy</button></td>'+
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



function join(){
{
        
        var username = document.getElementById("input-username").value;
        var password = document.getElementById("input-password").value;

          $.ajax({
    url: '/api/login',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { "username": username, "password": password} ),
    processData: false,
    success: function( data, textStatus, jQxhr ){
        myObjStr = JSON.stringify(data);
        json = JSON.parse(myObjStr)
        error = json['Error']

        if(! isEmptyObject(error)){
        alertify.error(json['Error']);
        }
        else{
            $(location).attr('href', '/lk')
        //alertify.success(json['User']['username']);
        }

    },
    error: function( jqXhr, textStatus, errorThrown ){
        console.log( errorThrown );
    }


});


}
}

$.ajax({

                  url: '/api/get_user',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    if(! isEmptyObject(jdata.Error)){
                      $("#auth").html('<span class="auth-text">Sign In</span><p><input type="text" class="login-field" style="width:100%" id="input-username" placeholder="Your login"></p><p><input type="text" class="password-field" style="width:100%" id="input-password" placeholder="Your password"></p><input class="submit-button" onClick="join()" type="submit" value="Join"><a href="register"><span class="register-button">Register >></span></a>');
                    } 
                    else{

                      $("#auth").html('<span class="auth-text" id="username"></span><p><span class="money" id="coins">$</span></p><p><a href="add_page" class="lk-links">Add merchandise</a></p><p><a href="orders" class="lk-links">My orders</a></p>  <p><a href="send_page" class="lk-links">Send money</a></p><p class="logout"><a href="" onClick="logout()">Logout</a></p>');

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


function buy(name){
{
        
        
        console.log(name)

          $.ajax({
    url: '/api/buy',
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
        $("#flags_table tbody").html("");
        $.ajax({

                  url: '/api/get_flags',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    var jsonData=jdata.flags
                    $(jsonData).each(function (index, item) {
                    $('#flags_table tbody').append(
                        '<tr><td>' + item.name+
                        '</td><td>' + item.cost +
                        '</td><td>' + item.in_stock +
                        '<td><button class="myButton" onClick="buy(' + "'" + item.name  + "'" + ')">buy</button></td>'+
                        '</td></tr>'
                    )
                });

                   },

                    error: function(errorThrown){
                    
                       console.log(errorThrown);
                    }

        }); 
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