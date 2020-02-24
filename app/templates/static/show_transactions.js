$.ajax({

                  url: '/api/get_user',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    if(! isEmptyObject(jdata.Error)){
                      $(location).attr('href', '/')
                    } 
                    else{
                      $("#auth").html('<span class="auth-text" id="username"></span><p><span class="money" id="coins">$</span></p><p><a href="add_page" class="lk-links">Add merchandise</a></p><p><a href="orders" class="lk-links">My orders</a></p>  <p><a href="send_page" class="lk-links send">Send money</a></p><p class="logout"><a href="" onClick="logout()">Logout</a></p>');

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

                  url: '/api/get_transactions',
                  method: "get",
                  dataType: "json",

                  success: function (jdata) {
                    var jsonData=jdata.transactions
                    $(jsonData).each(function (index, item) {
                    $('#translations_table tbody').append(
                        '<tr><td>' + item.from_user_id+
                        '</td><td>' + item.to_user_id +
                        '</td><td>' + item.msg +
                        '</td><td>' + item.value +
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



function send(){
{
        
        var username = document.getElementById("input-username").value;
        var value = document.getElementById("input-value").value;
        var msg = document.getElementById("input-msg").value;


        

          $.ajax({
    url: '/api/send',
    dataType: 'json',
    type: 'post',
    contentType: 'application/json',
    data: JSON.stringify( { "receiver": username, "value": value, "msg": msg} ),
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
        $('#translations_table tbody').append(
                        '<tr id="'+ username  +'"><td>' + username +
                        '</td><td>' + username +
                        '</td><td>' + value +
                        '</td><td>' + msg +
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